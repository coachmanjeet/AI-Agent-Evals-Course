"""Retrieval and generation metrics for RAG agents (Chapter 15)."""


def context_precision(retrieved, relevant):
    return sum(d in relevant for d in retrieved) / len(retrieved) if retrieved else 0.0


def context_recall(retrieved, relevant):
    return sum(d in set(retrieved) for d in relevant) / len(relevant) if relevant else 1.0


def faithfulness(claims_supported):
    """claims_supported: {claim: bool}, judged against the retrieved text."""
    return sum(claims_supported.values()) / len(claims_supported) if claims_supported else 1.0
