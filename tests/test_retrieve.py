import pandas as pd
import numpy as np
from typing import List
from ast import literal_eval
import matplotlib.pyplot as plt


def _pk(r, k):
    return sum(r[:k]) >= 1


def pk(documents_relevancy, k) -> float:
    return np.mean([_pk(r, k=k) for r in documents_relevancy])


def precision_at_k(r, k) -> float:
    assert k >= 1
    r = np.asarray(r[:k]) != 0
    if len(r) < k:
        return 0.0
    return np.mean(r)


def average_precision(r):
    r = np.asarray(r) != 0
    out = [precision_at_k(r, k + 1) for k in range(len(r)) if r[k]]
    if not out:
        return 0.0
    return np.mean(out)


def mean_average_precision(documents_relevancy) -> float:
    return np.mean([average_precision(r) for r in documents_relevancy])


def compute_metrics_from_df(df: pd.DataFrame):
    documents_relevancy = []
    grouped = df.groupby("question")

    for _, group in grouped:
        rel = group["is_link_relevant"].apply(
            lambda x: literal_eval(str(x)) if isinstance(x, (str, int, float)) else x
        ).tolist()
        rel_flattened = [item for sublist in rel for item in (sublist if isinstance(sublist, list) else [sublist])]
        documents_relevancy.append(rel_flattened)

    precision_values = {f"p@{k}": pk(documents_relevancy, k) for k in [1, 2, 3, 4, 5, 10]}
    map_value = mean_average_precision(documents_relevancy)

    print("Precision at k:")
    for k, v in precision_values.items():
        print(f"{k}: {v:.4f}")

    print(f"Mean Average Precision (MAP): {map_value:.4f}")

    plt.figure(figsize=(10, 6))
    plt.bar(precision_values.keys(), precision_values.values(), color='b')
    plt.title("Precision at k")
    plt.ylabel("Precision")
    plt.xlabel("k")
    plt.savefig('Precision_at_k.png', dpi=300)
    plt.show()
