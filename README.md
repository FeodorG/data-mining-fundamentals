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

### Lab 3 — Decision Tree Classification

Implementation of a decision tree classifier for the UCI Adult (Census Income)
dataset. The project includes:

- support for Information Gain, Gain Ratio, and Gini Index split criteria;
- classification of annual income into `<=50K` and `>50K` classes;
- configurable training-set proportion and tree depth;
- accuracy, precision, recall, and F1 evaluation;
- experiments with training/test splits from 60:40 to 90:10;
- decision-tree and classification-quality visualizations;
- CSV and JSON exports together with a PDF report.

On the official Adult split, Information Gain achieved the best F1 score of
approximately 0.630 and an accuracy of approximately 0.851.

Project folder: [`lab3`](lab3/)

## Environment

- Python 3.10 or newer
- dependencies are listed in each lab's `requirements.txt`
- Graphviz is required to render the decision trees in Lab 3

See [`lab1/README.md`](lab1/README.md), [`lab2/README.md`](lab2/README.md), and
[`lab3/README.md`](lab3/README.md) for commands and project structure.
