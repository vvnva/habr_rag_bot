import pandas as pd
import matplotlib.pyplot as plt

from typing import List


def pk(relevances: List[int], k: int) -> float:
    """Calculate Precision at k."""
    # if k > len(relevances):
    #     raise ValueError(f"k={k} exceeds the number of relevance scores provided.")
    return sum(relevances[:k]) / k


def mean_average_precision(relevances: List[int]) -> float:
    """Calculate Mean Average Precision."""
    ap_values = [pk(relevances, i) for i in range(1, len(relevances) + 1) if relevances[i - 1] == 1]
    return sum(ap_values) / sum(relevances) if sum(relevances) > 0 else 0


def process_queries(df: pd.DataFrame, retriever):
    """Process queries and calculate relevance and context."""
    relevances, contexts = [], []

    for question, links in zip(df["question"], df["gold_urls"]):
        query = f"{question}"
        retrieved_docs = retriever.get_relevant_documents(query)

        retrieved_links = [doc.metadata['link'] for doc in retrieved_docs]
        contexts.append('\n'.join(retrieved_links))

        relevance = [1 if link in retrieved_links else 0 for link in links]
        relevances.append(relevance)

    return relevances


def show_statistics(df: pd.DataFrame, retriever) -> None:
    """Process queries, calculate relevance, and display statistics."""
    relevances = process_queries(df, retriever)

    all_pk_values = {}
    map_values = []

    for relevance in relevances:
        pk_values = {f"pk@{k}": pk(relevance, k=k) for k in [1, 2, 3, 4, 5, 10] if k <= len(relevance)}
        map_values.append(mean_average_precision(relevance))

        for key, value in pk_values.items():
            all_pk_values.setdefault(key, []).append(value)

    avg_pk_values = {key: sum(values) / len(values) for key, values in all_pk_values.items()}
    avg_map_value = sum(map_values) / len(map_values)

    print("Statistics:")
    print(f"Precision at k: {avg_pk_values}")
    print(f"Mean Average Precision: {avg_map_value}")

    plt.figure(figsize=(10, 8))
    plt.bar(avg_pk_values.keys(), avg_pk_values.values(), color='b')
    plt.title("Average Precision at k")
    plt.ylabel("Precision")
    plt.xlabel("k")
    plt.savefig("stat.png", dpi=300)
    plt.show()


