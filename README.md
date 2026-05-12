# Article 126 IJNAMG Internal Erosion DEM-FEM Benchmark

This repository contains the reproducible computational evidence for the manuscript "Risk-Activated Hybrid DEM-FEM Model for Internal-Erosion Warning in Earth Dams".

## Contents

- `code/reproduce_article_126_clean.py`: script used to regenerate benchmark data, figures, tables and the manuscript working artifacts.
- `data/`: CSV and JSON benchmark outputs.
- `figures/`: figure PNG files generated from the benchmark.
- `tables/`: Excel workbook with manuscript tables.

## Reproduction

Run the script with Python 3 and the packages `numpy`, `pandas`, `matplotlib`, `python-docx`, `lxml`, and `openpyxl`.

```powershell
python code/reproduce_article_126_clean.py
```

The benchmark is synthetic and intended for numerical verification of the proposed risk-activated multiscale screening framework. It is not a calibrated operational dam-safety model.

