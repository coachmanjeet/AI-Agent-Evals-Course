#!/bin/bash
# Fleet PR fast check for AI-Agent-Evals-Course.
#
# Usage:
#   scripts/fast_check.sh [--all] [BASE]
#
# Default mode checks files changed between BASE and HEAD. BASE defaults
# to the merge-base of origin/main and HEAD, so on a PR branch this is
# exactly the PR diff. With --all, every tracked file is checked instead.
#
# Checks:
#   1. Every Python file in scope compiles (no bytecode is written into
#      the tree; compilation output goes to a temp dir).
#   2. No file in scope contains the banned terms named in the issue.
#      The pattern is built from parts at runtime so this script does
#      not flag its own source.
#
# Fast by design: no model calls, no keys, no installs. Exit 0 on pass,
# 1 on any failure.
set -u

# Built from parts so the literal terms never appear in this file.
BANNED_RE='RAG''AS|Deep''Eval'

ALL=0
BASE=""
for arg in "$@"; do
  case "$arg" in
    --all) ALL=1 ;;
    *) BASE="$arg" ;;
  esac
done

LIST_FILE=$(mktemp)
CACHE_DIR=$(mktemp -d)
trap 'rm -f "$LIST_FILE"; rm -rf "$CACHE_DIR"' EXIT

if [ "$ALL" -eq 1 ]; then
  git ls-files > "$LIST_FILE"
else
  if [ -z "$BASE" ]; then
    BASE=$(git merge-base origin/main HEAD 2>/dev/null || echo "origin/main")
  fi
  git diff --name-only --diff-filter=ACMR "$BASE" HEAD > "$LIST_FILE"
fi

if [ ! -s "$LIST_FILE" ]; then
  echo "fast_check: no files to check. PASS"
  exit 0
fi

FAIL=0

echo "fast_check: compiling Python files in scope..."
while IFS= read -r f; do
  case "$f" in
    *.py)
      if [ -f "$f" ]; then
        if ! python3 -c 'import py_compile, sys; py_compile.compile(sys.argv[1], cfile=sys.argv[2], doraise=True)' "$f" "$CACHE_DIR/check.pyc" 2>&1; then
          echo "fast_check: COMPILE FAIL: $f"
          FAIL=1
        fi
      fi
      ;;
  esac
done < "$LIST_FILE"

echo "fast_check: scanning for banned terms..."
while IFS= read -r f; do
  if [ -f "$f" ]; then
    if grep -qI -E "$BANNED_RE" "$f" 2>/dev/null; then
      echo "fast_check: BANNED TERM in $f:"
      grep -nI -E "$BANNED_RE" "$f"
      FAIL=1
    fi
  fi
done < "$LIST_FILE"

if [ "$FAIL" -ne 0 ]; then
  echo "fast_check: FAIL"
  exit 1
fi
echo "fast_check: PASS"
exit 0
