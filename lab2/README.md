# Поиск ассоциативных правил (Apriori)

Проект находит частые наборы и строит по ним ассоциативные правила. Для каждого правила выводятся антецедент, консеквент, поддержка и достоверность. Результат можно сортировать по убыванию поддержки или лексикографически.

## Установка зависимостей

```bash
python3 -m pip install -r requirements.txt
```

## Запуск программы

```bash
python3 src/apriori.py data/baskets.csv \
  --min-support 1 \
  --min-confidence 25 \
  --order support \
  --max-rule-size 7 \
  --itemsets-output results/itemsets_01pct.csv \
  --rules-output results/rules_25pct.csv
```

Пороги можно задавать долей (`0.01`, `0.25`) или процентом (`1`, `25`). Параметр `--order` принимает значения `support` и `lexicographic`. Ограничение `--max-rule-size` необязательно.

## Эксперименты и отчёт

```bash
python3 src/run_experiments.py
python3 src/build_report.py
```

В экспериментах поддержка зафиксирована на уровне 1%, а достоверность меняется от 25% до 50% с шагом 5%. Этот диапазон выбран потому, что на исходном наборе максимальная достоверность равна примерно 50,7%; диапазон 70-95% дал бы только нулевые результаты.

Готовый отчёт: `output/pdf/report_association_rules.pdf`.

## Структура

- `src/apriori.py` - Apriori, генерация правил и интерфейс командной строки;
- `src/run_experiments.py` - серия замеров, CSV-файлы и диаграммы;
- `src/build_report.py` - сборка PDF-отчёта;
- `data/baskets.csv` - исходные транзакции;
- `results/rules_*.csv` - правила для каждого порога достоверности;
- `results/rules_upto7.csv` - полный список правил длиной до семи объектов;
- `results/rules_runtime.png`, `results/rules_count.png` - диаграммы;
- `output/pdf/` - готовый PDF-отчёт.
