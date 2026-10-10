# DECODE session — plan evals with your PM in 90 minutes

## The idea in one sentence
Most eval plans fail because the PM's requirement ("handle damaged-item
refunds well") never got translated into gradable claims. DECODE is a 90-minute
working session — PM + eval engineer, one feature — that produces an eval plan.

## The agenda
| Time | Step | Output |
|---|---|---|
| 0:00–0:15 | **Scan** the requirement for compressed phrases — words doing too much work ("well," "accurately," "quickly") | Flagged phrase list |
| 0:15–0:35 | **Decompose** into atomic claims — single checkable statements | Numbered claim list |
| 0:35–0:55 | **Enumerate** modalities and slices — text, photo, audio; plus high-risk slices (blurry photos, non-English, edge cases) | Modality inventory |
| 0:55–1:15 | **Assign** each claim a contract (ingestion, faithfulness, cross-modal…) and name its failure modes | Draft eval plan |
| 1:15–1:30 | **Complete** the plan, sign off, name an eval owner | Finished plan + owner |

## Pronto example (damaged-item photo refunds)
- Compressed phrase: "correctly assess the damage" — correct *how*? Visible
  damage only? What about "arrived late but intact"?
- Atomic claims: (1) identifies the item in the photo; (2) describes visible
  damage accurately; (3) cites the right policy section; (4) refunds the right
  amount; (5) escalates if the photo is unclear.
- Modalities: text + photo. High-risk slices: blurry photos, multi-item photos,
  screenshots instead of photos.
- Contracts: claim 1 → ingestion fidelity; claim 2 → cross-modal consistency;
  claims 3–4 → faithfulness/factuality; claim 5 → escalation check.
- Failure modes named per claim: "photo shows box damage, agent refunds the
  item," "agent approves refund above the limit," "agent can't see, guesses
  anyway."

## The rule that matters
No claim leaves the room without an owner and a contract. "We'll figure out
how to test that later" is how eval gaps are born.
