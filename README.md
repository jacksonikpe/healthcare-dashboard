# Healthcare Analytics — Executive Overview (Streamlit)

## Windows / VS Code setup

1. Open the `healthcare-dashboard` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment: `py -m venv .venv`
4. Activate it in PowerShell: `.\.venv\Scripts\Activate.ps1`
   - If PowerShell blocks activation, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.\.venv\Scripts\python.exe -m streamlit run app.py` instead. This does not require activation.
5. Install packages: `python -m pip install -r requirements.txt`
6. Run: `python -m streamlit run app.py`
7. Open the local URL printed in the terminal, usually `http://localhost:8501`.
8. Stop with **Ctrl+C**.

## Project structure

```
healthcare-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── Patients_Data_Cleaned.csv
└── tests/
    └── test_data.py
```

The original cleaned CSV is provided in `data/` in the complete ZIP. If you only download `app.py`, copy your original `Patients_Data_Cleaned(Cleaned_Data).csv` into `data/` and rename it to `Patients_Data_Cleaned.csv`.

## Dashboard

- 4 colour-coded condition cards
- 6 interactive Plotly charts
- 6 shared multi-select filters + Reset
- Condition selector for the within-sex comparison
- Hover tooltips, selected-record count, CSV export, methods notes

**Notes:** This is the Executive Overview. Dedicated Heart Attack, Skin Cancer, Stroke and COPD pages can be added next. All statistics are computed from the actual cleaned CSV, not from the example screenshot. The dashboard is descriptive; it does not establish causal or population-representative findings.

## Assessment

Confirm with your module tutor that **Streamlit** is an approved dashboard tool. Include an accurate AI-use declaration, validate all claims and record a live walkthrough of the interactive dashboard.
