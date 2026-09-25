from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from adult_tree import DecisionTree, classification_metrics, load_adult, stratified_split, xy


ROOT = Path(__file__).resolve().parents[1]
COLORS = {"accuracy": "#264653", "precision": "#e76f51", "recall": "#2a9d8f", "f1": "#e9c46a"}


def font(size: int, bold: bool = False):
    path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
    return ImageFont.truetype(path, size)


def plot_metrics(rows: list[dict], output: Path) -> None:
    width, height = 1500, 900
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = 185, 120, 1420, 730
    draw.text((width // 2, 42), "Качество классификации в зависимости от доли обучения", fill="#1d3557", font=font(32, True), anchor="ma")
    for value in np.arange(0.55, 0.91, 0.05):
        y = bottom - (value - 0.55) / 0.35 * (bottom - top)
        draw.line((left, y, right, y), fill="#d9e2ec", width=2)
        draw.text((left - 18, y), f"{value:.2f}", fill="#334e68", font=font(22), anchor="rm")
    draw.line((left, top, left, bottom), fill="#334e68", width=3)
    draw.line((left, bottom, right, bottom), fill="#334e68", width=3)
    ratios = [r["train_ratio"] for r in rows]
    xs = [left + i * (right - left) / (len(ratios) - 1) for i in range(len(ratios))]
    for x, ratio in zip(xs, ratios):
        draw.line((x, bottom, x, bottom + 10), fill="#334e68", width=3)
        train_percent = round(ratio * 100)
        draw.text((x, bottom + 24), f"{train_percent}:{100-train_percent}", fill="#334e68", font=font(22), anchor="ma")
    for metric, color in COLORS.items():
        points = [(x, bottom - (row[metric] - 0.55) / 0.35 * (bottom - top)) for x, row in zip(xs, rows)]
        draw.line(points, fill=color, width=6, joint="curve")
        for x, y in points:
            draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=color, outline="white", width=2)
    draw.text(((left + right) // 2, 825), "Соотношение обучающей и тестовой выборок", fill="#334e68", font=font(24, True), anchor="mm")
    draw.text((92, (top + bottom) // 2), "Значение", fill="#334e68", font=font(24, True), anchor="mm")
    legend_x = 245
    for metric, color in COLORS.items():
        draw.line((legend_x, 92, legend_x + 45, 92), fill=color, width=6)
        draw.text((legend_x + 58, 92), metric, fill="#243b53", font=font(21), anchor="lm")
        legend_x += 245
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def render_tree(tree: DecisionTree, output: Path, criterion: str) -> None:
    dot_path = output.with_suffix(".dot")
    tree.export_dot(dot_path, display_depth=4)
    subprocess.run(["dot", "-Tpng", "-Gdpi=160", str(dot_path), "-o", str(output)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=ROOT / "data" / "adult.data.txt")
    parser.add_argument("--test", type=Path, default=ROOT / "data" / "adult.test.txt")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--max-depth", type=int, default=8)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    official_train = load_adult(args.train)
    official_test = load_adult(args.test)
    x_train, y_train = xy(official_train)
    x_test, y_test = xy(official_test)
    criterion_rows = []
    for criterion in ("information_gain", "gain_ratio", "gini"):
        print(f"Training {criterion} on official split...", flush=True)
        tree = DecisionTree(criterion=criterion, max_depth=args.max_depth).fit(x_train, y_train)
        metrics = classification_metrics(y_test, tree.predict(x_test))
        row = {"criterion": criterion, "train_size": len(official_train), "test_size": len(official_test), **metrics}
        criterion_rows.append(row)
        (out / f"tree_{criterion}.json").write_text(json.dumps(tree.to_dict(), indent=2), encoding="utf-8")
        render_tree(tree, out / f"tree_{criterion}.png", criterion)
    with (out / "criterion_metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=criterion_rows[0].keys())
        writer.writeheader(); writer.writerows(criterion_rows)

    import pandas as pd
    all_data = pd.concat([official_train, official_test], ignore_index=True)
    ratio_rows = []
    for ratio in (0.6, 0.7, 0.8, 0.9):
        print(f"Training gini with ratio {ratio:.1f}...", flush=True)
        train, test = stratified_split(all_data, ratio, seed=42)
        xt, yt = xy(train); xv, yv = xy(test)
        tree = DecisionTree(criterion="gini", max_depth=args.max_depth).fit(xt, yt)
        metrics = classification_metrics(yv, tree.predict(xv))
        ratio_rows.append({"train_ratio": ratio, "test_ratio": 1-ratio, "train_size": len(train), "test_size": len(test), **metrics})
    with (out / "split_metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=ratio_rows[0].keys())
        writer.writeheader(); writer.writerows(ratio_rows)
    plot_metrics(ratio_rows, out / "metrics_by_split.png")
    (out / "summary.json").write_text(json.dumps({"criteria": criterion_rows, "splits": ratio_rows}, indent=2), encoding="utf-8")
    print(json.dumps({"criteria": criterion_rows, "splits": ratio_rows}, indent=2))


if __name__ == "__main__":
    main()
