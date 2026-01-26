# Quick Start Guide

Get up and running with the Medicare RCM Analysis in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Basic command line knowledge
- ~2GB free disk space (for data)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/medicare-rcm-analysis.git
cd medicare-rcm-analysis
```

### 2. Set Up Python Environment

**Option A: Using venv (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option B: Using conda**
```bash
conda create -n rcm python=3.9
conda activate rcm
pip install -r requirements.txt
```

### 3. Download Data

Download CMS SynPUF carrier claims data:

1. Visit: https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs
2. Download: **DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv**
3. Place in: `data/raw/carrier01.csv`

**Alternative**: Use the smaller sample data (if available):
```bash
# If sample data is provided in the repo
cp data/sample/carrier_sample.csv data/raw/carrier01.csv
```

### 4. Run the Analysis

```bash
python src/rcm_analysis.py
```

**Expected output:**
```
============================================================
MEDICARE REVENUE CYCLE MANAGEMENT ANALYSIS
============================================================

Loading data...
✓ Loaded 1,121,004 records with 96 columns

Cleaning and validating data...
  - Duplicates found: 0
  - Financial logic violations: 1585 (0.14%)
  - 2022 records: 174,645
  - Clean dataset: 174,411 records (0.13% excluded)
✓ Data cleaning complete

Calculating revenue metrics...
✓ Metrics calculated

Analyzing HCPCS codes...
  - Top 5 codes account for $3.07M leakage
  - Top 2 codes account for 42.0% of total
✓ HCPCS analysis complete

... [continues]

✅ Analysis complete!
```

### 5. View Results

Results are saved in:
- **Excel Dashboard**: `results/RCM_Analysis_Final.xlsx`
- **CSV Files**: `results/*.csv`
- **Visualizations**: `results/figures/*.png`

Open the Excel file to see the full executive dashboard!

---

## What You Get

### Outputs

| File | Description |
|------|-------------|
| `RCM_Analysis_Final.xlsx` | Executive dashboard with 5 tabs |
| `hcpcs_summary.csv` | Procedure-level analysis |
| `specialty_summary.csv` | Specialty-level metrics |
| `high_risk_services.csv` | Flagged high-risk codes |
| `figures/revenue_waterfall.png` | Revenue flow visualization |
| `figures/pareto_hcpcs.png` | Top leakage drivers |
| `figures/payment_distribution.png` | Zero vs partial paid |

### Key Findings (from sample data)

-  **$5.48M** revenue leakage identified
-  **42%** concentrated in 2 codes
-  **77.8%** realization rate
-  **12** high-risk services
-  **$800K-$1.1M** recovery potential

---

## Troubleshooting

### "File not found" error

```bash
# Make sure data file is in the right location
ls data/raw/carrier01.csv

# If not, check your download location
```

### "Module not found" error

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Memory issues with large files

```python
# Edit src/rcm_analysis.py and add this at the top of load_data():
# self.df = pd.read_csv(self.data_path, header=None, nrows=100000)
# This limits to first 100K rows for testing
```

### Excel file won't open

```bash
# Install openpyxl if missing
pip install openpyxl
```

---

## Next Steps

### Customize the Analysis

**1. Change year filter:**
```python
# In src/rcm_analysis.py, line ~85
df_2022 = df[df["SERVICE_YEAR"] == 2021].copy()  # Change year
```

**2. Adjust risk thresholds:**
```python
# In src/rcm_analysis.py, identify_risks() method
(hcpcs_summary["realization_rate"] < 0.85)  # Lower threshold
```

**3. Add more visualizations:**
```python
# In generate_visualizations() method, add:
plt.figure(figsize=(10, 6))
plt.hist(df["REALIZATION_RATE"], bins=50)
plt.title("Realization Rate Distribution")
plt.savefig(f'{output_dir}/realization_dist.png', dpi=300)
plt.close()
```

### Use the Jupyter Notebook

For interactive exploration:

```bash
jupyter notebook notebooks/RCM_Analysis.ipynb
```

This gives you cell-by-cell control and inline visualizations.

### Integrate Your Own Data

Replace the CMS data with your own:

1. Format your data with same column names
2. Place in `data/raw/your_data.csv`
3. Update `DATA_PATH` in `src/rcm_analysis.py`
4. Run analysis

**Required columns:**
- `CLM_ID`, `LINE_NUM` (identifiers)
- `LINE_SBMTD_CHRG_AMT`, `LINE_ALOWD_CHRG_AMT`, `LINE_NCH_PMT_AMT` (financial)
- `LINE_1ST_EXPNS_DT`, `NCH_WKLY_PROC_DT` (dates)
- `HCPCS_CD`, `PRVDR_SPCLTY` (classification)

---

## Command Reference

```bash
# Fresh install
git clone <repo>
cd medicare-rcm-analysis
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run analysis
python src/rcm_analysis.py

# Run tests (if available)
pytest tests/

# Generate documentation
cd docs
make html  # If Sphinx is set up

# Clean outputs
rm -rf results/*.xlsx results/*.csv results/figures/*.png

# Deactivate virtual environment
deactivate
```

---

## Project Structure Quick Reference

```
├── data/
│   ├── raw/              ← Put your CSV here
│   └── outputs/          ← Generated CSVs
│
├── src/
│   └── rcm_analysis.py   ← Main script (run this)
│
├── results/
│   ├── RCM_Analysis_Final.xlsx  ← Main output
│   └── figures/          ← Charts & graphs
│
└── notebooks/
    └── RCM_Analysis.ipynb    ← Interactive version
```

---

## Performance Tips

**For large datasets (1M+ rows):**

1. **Use sampling for testing:**
   ```python
   df = pd.read_csv(file, nrows=100000)  # Test with 100K rows first
   ```

2. **Optimize memory:**
   ```python
   df = pd.read_csv(file, low_memory=False, dtype={'HCPCS_CD': 'category'})
   ```

3. **Use chunking:**
   ```python
   chunks = pd.read_csv(file, chunksize=50000)
   for chunk in chunks:
       process(chunk)
   ```

4. **Enable progress bars:**
   ```python
   from tqdm import tqdm
   tqdm.pandas()
   df.progress_apply(lambda x: x)
   ```

---

## Success Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Data file in `data/raw/carrier01.csv`
- [ ] Script runs without errors
- [ ] Excel file created in `results/`
- [ ] Visualisations generated in `results/figures/`
- [ ] Console shows executive summary

If all checks out, you're ready to go! 🚀

---

## What's Next?

After a successful run:

1.  **Review the Excel dashboard** - Start with Executive Summary tab
2.  **Examine visualisations** - Look at the Pareto chart for quick insights
3.  **Identify priorities** - Check Top Opportunities tab
4.  **Customize analysis** - Adjust thresholds or add metrics
5.  **Prepare presentation** - Use for interviews, reports, or demos

---

**Time to First Results**: ~15 minutes  
**Difficulty Level**: Beginner-friendly  
**Support**: Community-driven

*Happy analysing! 📈*