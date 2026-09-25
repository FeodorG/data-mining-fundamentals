# Data Mining Fundamentals

Course repository for practical assignments in **Data Mining Fundamentals**.

## Assignments

### Lab 1 — Frequent Itemset Mining

Implementation of the Apriori algorithm for supermarket basket analysis. The project includes:

- configurable minimum support and result ordering;
- experiments for support thresholds of 1%, 3%, 5%, 10%, and 15%;
- runtime and frequent-itemset visualizations;
- a PDF report with methodology and interpretation of results.

Project folder: [`lab1`](lab1/)

### Lab 2 — Association Rule Mining

Extension of the Apriori implementation that generates association rules from
frequent itemsets. The project includes:

- configurable minimum support, minimum confidence, result ordering, and rule size;
- experiments with a fixed support threshold of 1% and confidence thresholds from
  25% to 50%;
- runtime and rule-count visualizations;
- a readable CSV export of rules with support and confidence;
- a PDF report with methodology and interpretation of the discovered associations.

The confidence range was selected for this dataset because its strongest rule has
a confidence of approximately 50.7%; thresholds of 70–95% produce no rules.

Project folder: [`lab2`](lab2/)

## Environment

- Python 3.10 or newer
- dependencies are listed in each lab's `requirements.txt`

See [`lab1/README.md`](lab1/README.md) and [`lab2/README.md`](lab2/README.md) for
commands and project structure.
