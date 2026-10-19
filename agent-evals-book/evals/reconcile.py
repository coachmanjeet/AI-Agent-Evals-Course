"""Daily reconciliation: the agent's action log against the system of record (Chapter 19)."""
from collections import Counter


def reconcile(agent_log, ledger):
    """agent_log: {incident: amount}; ledger: [(incident, amount), ...]"""
    posted = Counter(incident for incident, _ in ledger)
    amounts = {incident: amount for incident, amount in ledger}
    return {"duplicates": [i for i, n in posted.items() if n > 1],
            "amount_mismatches": [i for i, a in agent_log.items() if i in amounts and amounts[i] != a],
            "missing_writes": [i for i in agent_log if i not in posted],
            "unexpected_writes": [i for i in posted if i not in agent_log]}
