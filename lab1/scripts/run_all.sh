#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "${PROJECT_DIR}"
"${PYTHON_BIN}" src/run_experiments.py
"${SCRIPT_DIR}/build_latex.sh"

echo "Эксперименты и LaTeX-отчёт успешно собраны."
