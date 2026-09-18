from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from time import perf_counter


def read_baskets(path: str | Path) -> list[frozenset[str]]:
    raw = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "cp1251"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Не удалось определить кодировку файла (ожидается UTF-8 или CP1251)")

    rows = csv.reader(text.splitlines())
    baskets = [frozenset(x.strip() for x in row if x.strip()) for row in rows]
    return [basket for basket in baskets if basket]


def apriori(
    transactions: list[frozenset[str]], min_support: float
) -> list[tuple[tuple[str, ...], int, float]]:
    if not 0 < min_support <= 1:
        raise ValueError("Порог поддержки должен принадлежать интервалу (0, 1]")
    n = len(transactions)
    if n == 0:
        return []
    min_count = math.ceil(min_support * n)

    counts = Counter(item for basket in transactions for item in basket)
    level = {frozenset([item]) for item, count in counts.items() if count >= min_count}
    all_frequent: list[tuple[tuple[str, ...], int, float]] = [
        ((next(iter(itemset)),), counts[next(iter(itemset))], counts[next(iter(itemset))] / n)
        for itemset in level
    ]

    k = 2
    while level:
        ordered = sorted(tuple(sorted(s)) for s in level)
        candidates: set[frozenset[str]] = set()
        for i, left in enumerate(ordered):
            for right in ordered[i + 1 :]:
                if left[: k - 2] != right[: k - 2]:
                    break
                candidate = frozenset(left) | frozenset(right)
                if len(candidate) == k and all(
                    frozenset(part) in level for part in combinations(candidate, k - 1)
                ):
                    candidates.add(candidate)
        if not candidates:
            break

        candidate_counts: Counter[frozenset[str]] = Counter()
        for basket in transactions:
            for candidate in candidates:
                if candidate <= basket:
                    candidate_counts[candidate] += 1
        level = {s for s, count in candidate_counts.items() if count >= min_count}
        all_frequent.extend(
            (tuple(sorted(s)), candidate_counts[s], candidate_counts[s] / n) for s in level
        )
        k += 1
    return all_frequent


def sort_itemsets(rows, order: str):
    if order == "support":
        return sorted(rows, key=lambda r: (-r[2], len(r[0]), r[0]))
    return sorted(rows, key=lambda r: (r[0], len(r[0])))


def save_results(path: str | Path, rows) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["itemset", "length", "support_count", "support"])
        for items, count, support in rows:
            writer.writerow(["; ".join(items), len(items), count, f"{support:.8f}"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Поиск частых наборов алгоритмом Apriori")
    parser.add_argument("dataset", help="CSV: одна корзина в строке, товары разделены запятыми")
    parser.add_argument("--min-support", type=float, required=True, help="Порог: доля (0..1) или процент (1..100)")
    parser.add_argument("--order", choices=("support", "lexicographic"), default="support")
    parser.add_argument("--output", default="frequent_itemsets.csv")
    args = parser.parse_args()

    threshold = args.min_support / 100 if args.min_support > 1 else args.min_support
    transactions = read_baskets(args.dataset)
    started = perf_counter()
    rows = sort_itemsets(apriori(transactions, threshold), args.order)
    elapsed = perf_counter() - started
    save_results(args.output, rows)
    print(f"Транзакций: {len(transactions)}")
    print(f"Частых наборов: {len(rows)}")
    print(f"Время: {elapsed:.6f} с")
    print(f"Результат: {args.output}")


if __name__ == "__main__":
    main()
