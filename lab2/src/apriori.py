from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from time import perf_counter


ItemsetRow = tuple[tuple[str, ...], int, float]
RuleRow = tuple[tuple[str, ...], tuple[str, ...], int, float, float]


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
) -> list[ItemsetRow]:
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


def generate_association_rules(
    frequent_itemsets: list[ItemsetRow], min_confidence: float
) -> list[RuleRow]:
    """Build all A -> B rules from frequent itemsets without rescanning baskets."""
    if not 0 < min_confidence <= 1:
        raise ValueError("Порог достоверности должен принадлежать интервалу (0, 1]")

    support_count = {frozenset(items): count for items, count, _ in frequent_itemsets}
    rules: list[RuleRow] = []
    for items, union_count, union_support in frequent_itemsets:
        if len(items) < 2:
            continue
        union = frozenset(items)
        for antecedent_size in range(1, len(items)):
            for antecedent_tuple in combinations(items, antecedent_size):
                antecedent = frozenset(antecedent_tuple)
                antecedent_count = support_count[antecedent]
                confidence = union_count / antecedent_count
                if confidence + 1e-15 >= min_confidence:
                    consequent = tuple(sorted(union - antecedent))
                    rules.append(
                        (
                            tuple(sorted(antecedent)),
                            consequent,
                            union_count,
                            union_support,
                            confidence,
                        )
                    )
    return rules


def sort_itemsets(rows, order: str):
    if order == "support":
        return sorted(rows, key=lambda r: (-r[2], len(r[0]), r[0]))
    return sorted(rows, key=lambda r: (r[0], len(r[0])))


def sort_rules(rows: list[RuleRow], order: str) -> list[RuleRow]:
    if order == "support":
        return sorted(rows, key=lambda r: (-r[3], -r[4], r[0], r[1]))
    return sorted(rows, key=lambda r: (r[0], r[1]))


def save_results(path: str | Path, rows) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["itemset", "length", "support_count", "support"])
        for items, count, support in rows:
            writer.writerow(["; ".join(items), len(items), count, f"{support:.8f}"])


def save_rules(path: str | Path, rows: list[RuleRow]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "antecedent",
                "consequent",
                "total_length",
                "support_count",
                "support",
                "confidence",
            ]
        )
        for antecedent, consequent, count, support, confidence in rows:
            writer.writerow(
                [
                    "; ".join(antecedent),
                    "; ".join(consequent),
                    len(antecedent) + len(consequent),
                    count,
                    f"{support:.8f}",
                    f"{confidence:.8f}",
                ]
            )


def format_rule(rule: RuleRow) -> str:
    antecedent, consequent, _, support, confidence = rule
    return (
        f"{{{', '.join(antecedent)}}} -> {{{', '.join(consequent)}}} "
        f"(поддержка: {support:.2%}, достоверность: {confidence:.2%})"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Поиск частых наборов и ассоциативных правил алгоритмом Apriori"
    )
    parser.add_argument("dataset", help="CSV: одна корзина в строке, товары разделены запятыми")
    parser.add_argument("--min-support", type=float, required=True, help="Порог: доля (0..1) или процент (1..100)")
    parser.add_argument("--min-confidence", type=float, required=True, help="Порог: доля (0..1) или процент (1..100)")
    parser.add_argument("--order", choices=("support", "lexicographic"), default="support")
    parser.add_argument("--itemsets-output", default="frequent_itemsets.csv")
    parser.add_argument("--rules-output", default="association_rules.csv")
    parser.add_argument(
        "--max-rule-size",
        type=int,
        default=None,
        help="Не выводить правила, где суммарное число объектов больше указанного",
    )
    args = parser.parse_args()

    support_threshold = args.min_support / 100 if args.min_support >= 1 else args.min_support
    confidence_threshold = (
        args.min_confidence / 100 if args.min_confidence >= 1 else args.min_confidence
    )
    transactions = read_baskets(args.dataset)
    started = perf_counter()
    itemsets = sort_itemsets(apriori(transactions, support_threshold), args.order)
    rules = generate_association_rules(itemsets, confidence_threshold)
    if args.max_rule_size is not None:
        if args.max_rule_size < 2:
            parser.error("--max-rule-size должен быть не меньше 2")
        rules = [r for r in rules if len(r[0]) + len(r[1]) <= args.max_rule_size]
    rules = sort_rules(rules, args.order)
    elapsed = perf_counter() - started
    save_results(args.itemsets_output, itemsets)
    save_rules(args.rules_output, rules)
    print(f"Транзакций: {len(transactions)}")
    print(f"Частых наборов: {len(itemsets)}")
    print(f"Ассоциативных правил: {len(rules)}")
    print(f"Время: {elapsed:.6f} с")
    print("\nПравила:")
    for rule in rules:
        print(format_rule(rule))
    print(f"\nЧастые наборы: {args.itemsets_output}")
    print(f"Правила: {args.rules_output}")


if __name__ == "__main__":
    main()
