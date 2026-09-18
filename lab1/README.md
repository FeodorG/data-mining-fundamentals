# Поиск частых наборов (Apriori)

Проект выполняет поиск частых наборов в `baskets.csv`, сохраняет поддержку каждого набора, проводит эксперименты для порогов 1%, 3%, 5%, 10% и 15% и строит диаграммы.

## Установка зависимостей

```bash
python3 -m pip install -r requirements.txt
```

## Запуск программы

```bash
python3 src/apriori.py data/baskets.csv --min-support 3 --order support --output results/itemsets_03pct.csv
python3 src/run_experiments.py
```

`--min-support` принимает долю (`0.03`) или процент (`3`). `--order` принимает `support` (по убыванию поддержки) или `lexicographic`.

## Сборка LaTeX-отчёта

Для сборки только отчёта требуется XeLaTeX:

```bash
./scripts/build_latex.sh
```

Полный запуск экспериментов и последующая сборка отчёта:

```bash
./scripts/run_all.sh
```

LaTeX-исходник находится в `latex/report.tex`, результат — в `output/pdf/report.pdf`.

## Структура

- `src/apriori.py` — реализация алгоритма и интерфейс командной строки;
- `src/run_experiments.py` — серия замеров и визуализация;
- `src/build_report.py` — альтернативная сборка отчёта через ReportLab;
- `latex/report.tex` — исходный текст LaTeX-отчёта;
- `scripts/` — сценарии автоматической сборки;
- `data/baskets.csv` — исходные транзакции;
- `results/` — таблицы результатов и диаграммы;
- `output/pdf/` — готовые PDF-отчёты.
