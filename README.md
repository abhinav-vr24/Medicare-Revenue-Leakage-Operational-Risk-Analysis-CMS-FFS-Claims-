# Medicare Revenue Cycle Management Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data Source](https://img.shields.io/badge/Data-CMS%20SynPUF-orange.svg)](https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs)

> A comprehensive revenue cycle performance analysis identifying $5.48M in revenue leakage and actionable optimization opportunities across 174K+ Medicare carrier claims.

## Project Overview

This project analyzes Medicare revenue cycle performance using CMS Synthetic Public Use Files (SynPUF) to identify revenue leakage drivers, payment patterns, and process inefficiencies. The analysis reveals critical insights including a **22.2% revenue leakage rate** and demonstrates that just **2 procedure codes account for 42% of total underpayment**.

### Key Findings

- **$5.48M** in revenue leakage identified (22.2% of allowed charges)
- **42%** of leakage concentrated in just 2 HCPCS codes (Pareto principle)
- **77.8%** realization rate vs 95-98% industry benchmark
- **75%** of leakage from partial payments (not denials)
- **$800K-$1.1M** estimated recoverable revenue (15-20% of total leakage)

## Quick Start

### Prerequisites

```bash
Python 3.8+
pandas
numpy
matplotlib
seaborn
openpyxl
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/medicare-rcm-analysis.git
cd medicare-rcm-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download CMS SynPUF data:
```bash
# Download from: https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs
# Place carrier claims file in data/raw/ directory
```

4. Run the analysis:
```bash
python src/rcm_analysis.py
```

## 📁 Project Structure

```
medicare-rcm-analysis/
│
├── data/
│   ├── raw/                      # Raw CMS data files (not tracked)
│   ├── processed/                # Cleaned datasets
│   └── outputs/                  # Analysis outputs (CSV files)
│
├── src/
│   ├── rcm_analysis.py          # Main analysis script
│   ├── data_cleaning.py         # Data validation and cleaning
│   ├── revenue_analysis.py      # Revenue realization metrics
│   ├── payment_analysis.py      # Payment pattern analysis
│   ├── delay_analysis.py        # Processing delay analysis
│   └── visualization.py         # Chart generation
│
├── notebooks/
│   └── RCM_Analysis.ipynb       # Interactive analysis notebook
│
├── results/
│   ├── RCM_Analysis_Final.xlsx  # Executive dashboard
│   ├── figures/                 # Generated visualizations
│   └── reports/                 # Analysis reports
│
├── docs/
│   ├── METHODOLOGY.md           # Detailed methodology
│   ├── DATA_DICTIONARY.md       # Field definitions
│   └── FINDINGS.md              # Detailed findings report
│
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
└── README.md                    # This file
```

## Analysis Framework

### 1. Data Cleaning & Validation
- **Uniqueness checks**: Validate (CLM_ID, LINE_NUM) combinations
- **Financial logic**: Ensure Submitted ≥ Allowed ≥ Paid
- **Date consistency**: Service date ≤ Processing date
- **Result**: 99.86% data quality (174,411 valid records)

### 2. Revenue Realization Analysis
**Key Metrics:**
- Realization Rate = (Paid / Allowed) × 100
- Underpayment = Allowed - Paid
- Collection Efficiency = Provider Payment / Allowed
- Denial Rate = 1 - Realization Rate

### 3. Payment Pattern Classification
- **Zero-Paid** (61.0%): Payment = $0 (denial proxy)
- **Partial-Paid** (33.4%): $0 < Payment < Allowed (adjustment)
- **Fully-Paid** (6.3%): Payment ≈ Allowed (normal processing)

### 4. Risk Identification
- **Pareto Analysis**: 80/20 concentration
- **Outlier Detection**: IQR method on underpayment & delay
- **Variation Analysis**: Coefficient of variation for process stability
- **Result**: 12 high-risk services flagged

## Key Visualizations

### Revenue Waterfall
Shows flow from Submitted ($24.68M) → Allowed ($24.68M) → Paid ($19.20M)

### Pareto Chart
Top 10 HCPCS codes by underpayment - demonstrates 42% concentration in 2 codes

### Payment Distribution
75% of leakage from partial payments vs 25% from denials

### AR Aging Profile
All claims in 0-30 day bucket (Medicare efficiency)

## Strategic Recommendations

### Priority 1: High Impact Quick Wins
**1. Target Top 5 HCPCS Codes**
- **Codes**: 96156, 94010, 99495, G8839, S9473
- **Impact**: $3.07M (56% of total leakage)
- **Action**: Deep-dive denial analysis, enhanced claims scrubbing
- **Expected Recovery**: $460K-$615K

### Priority 2: Systemic Improvements
**2. Optimize Partial Payment Recovery**
- **Impact**: $4.11M opportunity (75% of leakage)
- **Action**: Systematic appeals process, contract renegotiation
- **Expected Impact**: Improve realization rate from 77.8% to 82-85%

**3. Address High-Risk Services**
- **Codes**: G8939 (48.3% denial), G8434 (35.6% denial)
- **Action**: Review documentation standards, targeted training
- **Expected Impact**: Reduce denial rate by 5-10 percentage points

### Priority 3: Process Excellence
**4. Specialty-Specific Protocols**
- **Focus**: Specialty 01 (24.2% denial rate vs 22.2% average)
- **Action**: Customized charge capture, documentation templates
- **Expected Impact**: Standardize performance across specialties

**5. Real-Time Monitoring**
- **Action**: Deploy automated dashboards, establish alerts
- **Expected Impact**: Reduce detection-to-action time by 50%

## Business Impact

### Financial Impact
- **Current State**: 77.8% realization rate
- **Target State**: 85%+ (industry benchmark)
- **Revenue Recovery**: $800K-$1.1M annually
- **ROI**: 3-4x within 12 months

### Operational Impact
- Reduced denial rate through targeted interventions
- Improved cash flow through faster AR resolution
- Enhanced provider satisfaction via reduced administrative burden
- Scalable framework applicable to any payer mix

## Technical Approach

### Data Processing Pipeline
```python
# 1. Load & Clean
df = load_cms_data('carrier_claims.csv')
df_clean = validate_financial_logic(df)
df_2022 = filter_by_year(df_clean, 2022)

# 2. Calculate Metrics
df_metrics = calculate_realization_metrics(df_2022)
df_metrics = classify_payment_status(df_metrics)

# 3. Aggregate & Analyze
hcpcs_summary = aggregate_by_hcpcs(df_metrics)
specialty_summary = aggregate_by_specialty(df_metrics)

# 4. Identify Risks
high_risk = detect_outliers(hcpcs_summary)
risk_priority = prioritize_interventions(high_risk)
```

### Statistical Methods
- **Descriptive Statistics**: Mean, median, quartiles, percentiles
- **Outlier Detection**: Interquartile range (IQR) method
- **Variation Analysis**: Coefficient of variation (CV)
- **Concentration Analysis**: Pareto (80/20) principle

## Data Source

**CMS Medicare Claims Synthetic Public Use Files (SynPUF)**
- Source: Centers for Medicare & Medicaid Services
- Type: De-identified synthetic beneficiary and claims data
- Coverage: 2008-2010 data (used 2022 synthetic extension)
- Volume: 174,411 carrier claim lines analyzed
- Link: [CMS SynPUF](https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs)

### Data Limitations
- Synthetic data may not reflect all real-world complexity
- Limited explicit denial reason codes
- Medicare only (no commercial payer mix)
- Accelerated processing times (4-day avg vs typical 30-90 days)

## Use Cases

### For Healthcare Organizations
- Benchmark revenue cycle performance
- Identify procedure-specific leakage drivers
- Prioritize denial prevention efforts
- Support contract negotiation with data

### For Analytics Teams
- Framework for RCM analysis
- Methodology for payment pattern analysis
- Approach to risk identification
- Template for executive reporting

### For Academic/Training
- Real-world healthcare data analysis example
- Revenue cycle management concepts
- Python data analysis techniques
- Business intelligence reporting

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is not licensed.

## Author

**Abhinav Verma**
- LinkedIn: www.linkedin.com/in/abhinavverma-mph-ha
- Email: abhinav.tiss01@gmail.com
- GitHub: [@abhinav-vr24](https://github.com/abhinav-vr24)

## Acknowledgments

- CMS for providing SynPUF dataset
- Healthcare Financial Management Association (HFMA) for industry benchmarks


---

**Note**: This analysis uses synthetic data for educational and demonstration purposes. Real-world healthcare data requires proper HIPAA compliance and data use agreements.

## Quick Stats

| Metric | Value |
|--------|-------|
| Claims Analyzed | 174,411 |
| Revenue Processed | $24.68M |
| Realization Rate | 77.8% |
| Revenue Leakage | $5.48M |
| Zero-Paid Rate | 61.0% |
| High-Risk Services | 12 codes |
| Recovery Potential | $800K-$1.1M |
| Analysis Date | January 2025 |

---

*Built with ❤️ for healthcare revenue cycle optimization*# Medicare-Revenue-Leakage-Operational-Risk-Analysis-CMS-FFS-Claims-
# Medicare-Revenue-Leakage-Operational-Risk-Analysis-CMS-FFS-Claims-
# Medicare-Revenue-Leakage-Operational-Risk-Analysis-CMS-FFS-Claims-
# Medicare-Revenue-Leakage-Operational-Risk-Analysis-CMS-FFS-Claims-
