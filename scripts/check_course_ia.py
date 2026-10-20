#!/usr/bin/env python3
"""Course information-architecture guardrail — see docs/course-architecture.md.

"One fact, one home": this script fails (exit 1, with a printed report) when:

(a) DOCX — any `.docx` file exists anywhere in the repo (excluding `.git`).
    Assignment instructions live only in repo markdown; a `.docx` is a
    second, drifting source. If a `.docx` is ever needed, generate it from
    the markdown at publish time and discard it.

(b) NEAR-DUPLICATE INSTRUCTIONS — near-duplicate instruction text appears
    in 2+ markdown files. Scope: "assignment-related" files only — every
    `.md` file under any `assignments/` directory, plus any `walkthrough.md`
    (week entry pages, examples stubs, and resource references are index /
    pointer material by design and are out of scope for this check).
    Heuristic (documented, intentionally conservative so deliberate starter
    templates that repeat a single sentence do not trip it):
      * prose is extracted with fenced code blocks removed, markdown
        punctuation stripped, and text lowercased;
      * word 8-gram "shingles" are built per file;
      * a pair of files is flagged when they share >= 20 shingles AND the
        shared shingles cover >= 8% of the smaller file's shingles
        (containment), OR they share >= 3 identical long lines
        (normalized lines of >= 80 characters).
    A flag means the same instructions are maintained in two places:
    keep the text in the assignment README and replace the other copy
    with a link.

(c) WEEK 1 FAILURE-CODE VOCABULARY — more than one failure-code vocabulary
    in use in the Week 1 sources (Assignment 2 README, Assignment 2
    starter, the student clarity guide, and datasets/README.md).
    Method: SCREAMING_SNAKE tokens (ALL_CAPS_WITH_UNDERSCORES) are
    extracted per file, minus a stoplist of non-codes (API-key env vars,
    the format name SCREAMING_SNAKE itself, template placeholders).
    A token whose every mention sits in a negation/deprecation context
    ("there is no `X`", "never `X`", "formerly", ...) is treated as a
    *blocklisted* (retired) name, not a live code. The check fails when:
      * 2+ members of a known competing-name family (e.g.
        HALLUCINATED_FACT vs HALLUCINATED_ORDER — same failure, two names)
        are in live use across the files, or
      * a blocklisted/retired code is in live use in any other file.
    Note: datasets/README.md's snake_case `failure_mode` column values are
    a dataset schema namespace, explicitly scoped as such in that file;
    the Week 1 annotation vocabulary checked here is the SCREAMING_SNAKE
    one, so only SCREAMING_SNAKE tokens are compared.

(d) ENTRY PAGES — any `week-0X-*` folder lacks a `README.md` entry page,
    or any `assignments/*/` folder lacks a `README.md`.

Usage:  python3 scripts/check_course_ia.py [repo-root]
Exit:   0 = all checks pass, 1 = one or more checks failed.
Stdlib only.
"""

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent

failures = []  # list of (check, message)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# ---------------------------------------------------------------- (a) .docx
def check_docx():
    hits = sorted(
        p for p in ROOT.rglob("*.docx")
        if ".git" not in p.parts
    )
    for p in hits:
        failures.append(("a-docx", f"{rel(p)} — .docx files are not allowed in the repo "
                                   f"(instructions live in markdown only; see docs/course-architecture.md)"))
    return len(hits)


# ------------------------------------------------- (b) near-duplicate text
SHINGLE_N = 8
MIN_SHARED_SHINGLES = 20
MIN_CONTAINMENT = 0.08
MIN_SHARED_LONG_LINES = 3
LONG_LINE_CHARS = 80


def prose_lines(path: Path):
    """Yield normalized prose lines, with fenced code blocks removed."""
    out = []
    in_fence = False
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"[`*_>#|]", " ", raw)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)  # links -> text
        line = re.sub(r"[^a-z0-9 ]+", " ", line.lower())
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            out.append(line)
    return out


def shingles(lines):
    words = " ".join(lines).split()
    return {" ".join(words[i:i + SHINGLE_N]) for i in range(len(words) - SHINGLE_N + 1)}


def assignment_related_md():
    files = []
    for p in sorted(ROOT.rglob("*.md")):
        if ".git" in p.parts:
            continue
        if "assignments" in p.parts or p.name == "walkthrough.md":
            files.append(p)
    return files


def check_duplicates():
    files = assignment_related_md()
    data = {}
    for p in files:
        lines = prose_lines(p)
        data[p] = {
            "shingles": shingles(lines),
            "long_lines": {ln for ln in lines if len(ln) >= LONG_LINE_CHARS},
        }
    flagged = 0
    for i, a in enumerate(files):
        for b in files[i + 1:]:
            shared_sh = data[a]["shingles"] & data[b]["shingles"]
            smaller = min(len(data[a]["shingles"]), len(data[b]["shingles"])) or 1
            containment = len(shared_sh) / smaller
            shared_lines = data[a]["long_lines"] & data[b]["long_lines"]
            if (len(shared_sh) >= MIN_SHARED_SHINGLES and containment >= MIN_CONTAINMENT) \
                    or len(shared_lines) >= MIN_SHARED_LONG_LINES:
                flagged += 1
                failures.append((
                    "b-duplicate",
                    f"{rel(a)}  <->  {rel(b)} — {len(shared_sh)} shared {SHINGLE_N}-word shingles "
                    f"({containment:.0%} of the smaller file), {len(shared_lines)} shared long lines. "
                    f"Keep the text in one home and link from the other.",
                ))
    return flagged


# --------------------------------------- (c) Week 1 failure-code vocabulary
CODE_RE = re.compile(r"[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+")
STOPLIST = {"SCREAMING_SNAKE", "YOUR_CODE_HERE"}
# Known competing-name families: same failure, different names (from the
# 2026-10-20 audit). Extend this list when a new rename happens.
COMPETING_FAMILIES = [
    {"HALLUCINATED_FACT", "HALLUCINATED_ORDER"},
]


def week1_vocab_sources():
    w1 = sorted(ROOT.glob("week-01-*"))
    if not w1:
        return []
    w1 = w1[0]
    candidates = [
        w1 / "assignments" / "02-failure-taxonomy" / "README.md",
        w1 / "assignments" / "02-failure-taxonomy" / "starter.md",
        w1 / "student-clarity-guide.md",
        ROOT / "datasets" / "README.md",
    ]
    return [p for p in candidates if p.exists()]


def _mention_negated(line: str, code: str) -> bool:
    """True if this specific mention of `code` is a negation/deprecation.

    Deliberately narrow (a bare "not" appears in ordinary definitions):
    a mention counts as retired only when a negation directly precedes the
    code ("there is no `X`", "never `X`", "do not use X") or a deprecation
    word directly follows it ("`X` is deprecated / formerly ...").
    """
    before = re.search(rf"(no|never|not|avoid|don'?t use|do not use)\s+`?{re.escape(code)}`?\b", line)
    after = re.search(rf"`?{re.escape(code)}`?[^\n.]{{0,40}}(deprecated|retired|formerly|old name)", line)
    return bool(before or after)


def live_and_retired_codes(path: Path):
    """Return (live_codes, retired_codes) for one file.

    A code is retired in a file if every mention of it in that file is a
    negation/deprecation mention; if it has any live mention, it is live.
    """
    mentions = {}  # code -> list of bools (True if that mention is negated)
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        for code in CODE_RE.findall(line):
            if code in STOPLIST or code.endswith("_API_KEY"):
                continue
            mentions.setdefault(code, []).append(_mention_negated(line, code))
    live = {c for c, flags in mentions.items() if not all(flags)}
    retired = {c for c, flags in mentions.items() if all(flags)}
    return live, retired


def check_week1_vocabulary():
    sources = week1_vocab_sources()
    if not sources:
        failures.append(("c-vocab", "Week 1 source files not found — cannot verify failure-code vocabulary"))
        return 1
    live_by_file, retired_all = {}, set()
    for p in sources:
        live, retired = live_and_retired_codes(p)
        live_by_file[p] = live
        retired_all |= retired
    flagged = 0
    # Competing families in live use anywhere across the files.
    live_union = set().union(*live_by_file.values()) if live_by_file else set()
    for family in COMPETING_FAMILIES:
        present = family & live_union
        if len(present) >= 2:
            flagged += 1
            failures.append((
                "c-vocab",
                f"Competing failure-code names in live use across Week 1 files: "
                f"{sorted(present)} — pick one name per failure and use it everywhere.",
            ))
    # A retired name used live anywhere is a second vocabulary leaking back.
    for p, live in live_by_file.items():
        bad = live & retired_all
        if bad:
            flagged += 1
            failures.append((
                "c-vocab",
                f"{rel(p)} uses {sorted(bad)} live, but that name is marked retired/never-use "
                f"in another Week 1 file — one failure-code vocabulary only.",
            ))
    # Diagnostic (not a failure): show each file's live set.
    print("  Week 1 live failure-code sets (diagnostic):")
    for p, live in live_by_file.items():
        print(f"    {rel(p)}: {sorted(live) if live else '(none)'}")
    if retired_all:
        print(f"    retired names mentioned: {sorted(retired_all)}")
    return flagged


# ------------------------------------------------------------ (d) entry pages
def check_entry_pages():
    flagged = 0
    weeks = sorted(p for p in ROOT.glob("week-0*") if p.is_dir())
    for week in weeks:
        if not (week / "README.md").exists():
            flagged += 1
            failures.append(("d-entry", f"{rel(week)}/ has no README.md entry page"))
        assignments = week / "assignments"
        if assignments.is_dir():
            for sub in sorted(p for p in assignments.iterdir()
                              if p.is_dir() and p.name != "__pycache__" and not p.name.startswith(".")):
                if not (sub / "README.md").exists():
                    flagged += 1
                    failures.append(("d-entry", f"{rel(sub)}/ has no README.md "
                                                f"(every assignment folder needs its one complete README)"))
    return flagged


def main():
    print(f"Course IA check — repo: {ROOT}")
    n_docx = check_docx()
    print(f"(a) .docx files found: {n_docx}")
    n_dup = check_duplicates()
    print(f"(b) near-duplicate assignment-file pairs flagged: {n_dup}")
    n_vocab = check_week1_vocabulary()
    print(f"(c) Week 1 failure-code vocabulary problems: {n_vocab}")
    n_entry = check_entry_pages()
    print(f"(d) missing entry-page READMEs: {n_entry}")

    if failures:
        print(f"\nFAIL — {len(failures)} problem(s):")
        for check, msg in failures:
            print(f"  [{check}] {msg}")
        return 1
    print("\nPASS — all course IA checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
