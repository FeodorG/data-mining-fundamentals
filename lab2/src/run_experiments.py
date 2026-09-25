from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from time import perf_counter

from PIL import Image, ImageDraw, ImageFont

from apriori import (
    apriori,
    generate_association_rules,
    read_baskets,
    save_results,
    save_rules,
    sort_itemsets,
    sort_rules,
)


ROOT = Path(__file__).resolve().parents[1]
MIN_SUPPORT = 0.01
CONFIDENCE_THRESHOLDS = (0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
REPEATS = 100


def font(size: int, bold: bool = False):
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    return ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{name}", size)


def draw_axes(draw, title, xlabel, ylabel, max_y, decimals=0):
    left, top, right, bottom = 150, 100, 1420, 750
    draw.text((785, 28), title, anchor="ma", font=font(32, True), fill="#17324d")
    draw.line((left, top, left, bottom), fill="#334e68", width=3)
    draw.line((left, bottom, right, bottom), fill="#334e68", width=3)
    for i in range(6):
        y = bottom - (bottom - top) * i / 5
        value = max_y * i / 5
        draw.line((left, y, right, y), fill="#d9e2ec", width=2)
        draw.text(
            (left - 15, y),
            f"{value:.{decimals}f}",
            anchor="rm",
            font=font(19),
            fill="#486581",
        )
    draw.text((785, 850), xlabel, anchor="mm", font=font(23), fill="#334e68")
    draw.text((24, 425), ylabel, anchor="lm", font=font(21), fill="#334e68")
    return left, top, right, bottom


def line_chart(rows, key, title, ylabel, path, decimals=0, value_format=None):
    image = Image.new("RGB", (1500, 900), "white")
    draw = ImageDraw.Draw(image)
    values = [float(r[key]) for r in rows]
    max_y = max(values) * 1.18 if max(values) else 1
    left, top, right, bottom = draw_axes(
        draw, title, "Минимальная достоверность", ylabel, max_y, decimals
    )
    xs = [left + (right - left) * (i + 0.5) / len(values) for i in range(len(values))]
    points = [(x, bottom - value / max_y * (bottom - top)) for x, value in zip(xs, values)]
    draw.line(points, fill="#2864a8", width=7)
    for i, ((x, y), value) in enumerate(zip(points, values)):
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill="#2864a8")
        label = value_format(value) if value_format else f"{value:.{decimals}f}"
        draw.text((x, y - 20), label, anchor="mb", font=font(18, True), fill="#17324d")
        draw.text(
            (x, bottom + 18),
            f"{float(rows[i]['confidence_threshold']) * 100:.0f}%",
            anchor="ma",
            font=font(21),
            fill="#334e68",
        )
    image.save(path)


def main() -> None:
    results_dir = ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    transactions = read_baskets(ROOT / "data" / "baskets.csv")
    frequent_itemsets = sort_itemsets(apriori(transactions, MIN_SUPPORT), "support")
    save_results(results_dir / "itemsets_01pct.csv", frequent_itemsets)

    summary = []
    for threshold in CONFIDENCE_THRESHOLDS:
        timings = []
        rules = None
        for _ in range(REPEATS):
            started = perf_counter()
            rules = generate_association_rules(frequent_itemsets, threshold)
            timings.append(perf_counter() - started)
        assert rules is not None
        rules = sort_rules(rules, "support")
        save_rules(results_dir / f"rules_{int(threshold * 100):02d}pct.csv", rules)
        summary.append(
            {
                "support_threshold": MIN_SUPPORT,
                "confidence_threshold": threshold,
                "median_seconds": statistics.median(timings),
                "min_seconds": min(timings),
                "max_seconds": max(timings),
                "rules": len(rules),
            }
        )

    representative_rules = sort_rules(
        [
            rule
            for rule in generate_association_rules(frequent_itemsets, CONFIDENCE_THRESHOLDS[0])
            if len(rule[0]) + len(rule[1]) <= 7
        ],
        "support",
    )
    save_rules(results_dir / "rules_upto7.csv", representative_rules)

    with (results_dir / "association_rule_summary.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)
    (results_dir / "association_rule_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    line_chart(
        summary,
        "median_seconds",
        "Время генерации ассоциативных правил",
        "Время, с",
        results_dir / "rules_runtime.png",
        decimals=4,
        value_format=lambda value: f"{value * 1000:.2f} мс",
    )
    line_chart(
        summary,
        "rules",
        "Количество найденных правил",
        "Правила",
        results_dir / "rules_count.png",
        decimals=0,
        value_format=lambda value: str(int(value)),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
