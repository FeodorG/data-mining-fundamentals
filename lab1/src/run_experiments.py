from __future__ import annotations

import csv
import json
import statistics
from collections import Counter
from pathlib import Path
from time import perf_counter

from PIL import Image, ImageDraw, ImageFont

from apriori import apriori, read_baskets, save_results, sort_itemsets


ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS = (0.01, 0.03, 0.05, 0.10, 0.15)
REPEATS = 3


def font(size: int, bold: bool = False):
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    return ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{name}", size)


def draw_axes(draw, title, xlabel, ylabel, max_y):
    left, top, right, bottom = 125, 80, 1420, 750
    draw.text((800, 25), title, anchor="ma", font=font(34, True), fill="#17324d")
    draw.line((left, top, left, bottom), fill="#334e68", width=3)
    draw.line((left, bottom, right, bottom), fill="#334e68", width=3)
    for i in range(6):
        y = bottom - (bottom - top) * i / 5
        value = max_y * i / 5
        draw.line((left, y, right, y), fill="#d9e2ec", width=2)
        draw.text((left - 15, y), f"{value:.2f}" if max_y < 10 else f"{value:.0f}", anchor="rm", font=font(20), fill="#486581")
    draw.text((770, 855), xlabel, anchor="mm", font=font(24), fill="#334e68")
    draw.text((58, 410), ylabel, anchor="mm", font=font(24), fill="#334e68", stroke_width=0)
    return left, top, right, bottom


def runtime_chart(rows, path):
    image = Image.new("RGB", (1500, 900), "white"); draw = ImageDraw.Draw(image)
    values = [r["median_seconds"] for r in rows]; max_y = max(values) * 1.15
    left, top, right, bottom = draw_axes(draw, "Время работы Apriori", "Минимальная поддержка", "Время, с", max_y)
    xs = [left + (right-left) * (i + .5) / len(values) for i in range(len(values))]
    pts = [(x, bottom - v / max_y * (bottom-top)) for x, v in zip(xs, values)]
    draw.line(pts, fill="#2864a8", width=7)
    for i, ((x, y), v) in enumerate(zip(pts, values)):
        draw.ellipse((x-10, y-10, x+10, y+10), fill="#2864a8")
        draw.text((x, y-22), f"{v:.4f}", anchor="mb", font=font(18, True), fill="#17324d")
        draw.text((x, bottom+18), f"{int(rows[i]['threshold']*100)}%", anchor="ma", font=font(22), fill="#334e68")
    image.save(path)


def length_chart(summary, length_rows, path):
    image = Image.new("RGB", (1500, 900), "white"); draw = ImageDraw.Draw(image)
    max_y = max(r["itemsets"] for r in summary) * 1.12
    left, top, right, bottom = draw_axes(draw, "Число частых наборов по длине", "Минимальная поддержка", "Количество", max_y)
    lengths = sorted({r["length"] for r in length_rows})
    colors = ["#2864a8", "#49a078", "#f0a202", "#d1495b", "#7353ba", "#5c677d"]
    width = (right-left) / len(summary) * .58
    for i, row in enumerate(summary):
        x0 = left + (right-left) * (i + .5) / len(summary) - width/2
        y = bottom
        for j, length in enumerate(lengths):
            value = next((x["count"] for x in length_rows if x["threshold"] == row["threshold"] and x["length"] == length), 0)
            h = value / max_y * (bottom-top)
            draw.rectangle((x0, y-h, x0+width, y), fill=colors[j % len(colors)])
            y -= h
        draw.text((x0+width/2, bottom+18), f"{int(row['threshold']*100)}%", anchor="ma", font=font(22), fill="#334e68")
        draw.text((x0+width/2, y-8), str(row["itemsets"]), anchor="mb", font=font(18, True), fill="#17324d")
    for j, length in enumerate(lengths):
        lx = 240 + j * 190
        draw.rectangle((lx, 805, lx+28, 833), fill=colors[j % len(colors)])
        draw.text((lx+38, 819), f"Длина {length}", anchor="lm", font=font(18), fill="#334e68")
    image.save(path)


def main() -> None:
    transactions = read_baskets(ROOT / "data" / "baskets.csv")
    rows_summary = []
    length_rows = []
    for threshold in THRESHOLDS:
        timings = []
        result = None
        for _ in range(REPEATS):
            started = perf_counter()
            result = apriori(transactions, threshold)
            timings.append(perf_counter() - started)
        assert result is not None
        result = sort_itemsets(result, "support")
        save_results(ROOT / "results" / f"itemsets_{int(threshold * 100):02d}pct.csv", result)
        by_length = Counter(len(items) for items, _, _ in result)
        rows_summary.append({
            "threshold": threshold,
            "median_seconds": statistics.median(timings),
            "min_seconds": min(timings),
            "max_seconds": max(timings),
            "itemsets": len(result),
            "max_length": max(by_length, default=0),
        })
        for length, count in sorted(by_length.items()):
            length_rows.append({"threshold": threshold, "length": length, "count": count})

    with (ROOT / "results" / "experiment_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows_summary[0].keys())
        writer.writeheader(); writer.writerows(rows_summary)
    with (ROOT / "results" / "itemsets_by_length.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=("threshold", "length", "count"))
        writer.writeheader(); writer.writerows(length_rows)
    (ROOT / "results" / "experiment_summary.json").write_text(
        json.dumps(rows_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    runtime_chart(rows_summary, ROOT / "results" / "runtime.png")
    length_chart(rows_summary, length_rows, ROOT / "results" / "itemsets_by_length.png")
    print(json.dumps(rows_summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
