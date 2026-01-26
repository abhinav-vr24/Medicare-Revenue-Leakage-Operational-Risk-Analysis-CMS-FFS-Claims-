# Analysis Methodology

## Overview

This document details the technical methodology used in the Medicare Revenue Cycle Management (RCM) Analysis project. The analysis follows a structured, multi-stage approach to ensure data quality, analytical rigor, and actionable insights.

## Data Pipeline

### Stage 1: Data Acquisition & Loading

**Source**: CMS Medicare Claims Synthetic Public Use Files (SynPUF)
- **File Type**: Carrier (physician/supplier) claims
- **Format**: Pipe-delimited CSV
- **Initial Volume**: 1,121,004 claim lines (2008-2022)
- **Fields**: 96 columns including demographics, financial, clinical, and administrative data

**Loading Process**:
```python
# Read raw data without headers
df = pd.read_csv("carrier_claims.csv", header=None)

# Extract column names from second row
df.columns = df.iloc[1]

# Remove metadata rows
df = df.drop([0,1]).reset_index(drop=True)
```

### Stage 2: Data Cleaning & Validation

#### 2.1 Uniqueness Validation
**Purpose**: Ensure each claim line is represented once
```python
# Validate (CLM_ID, LINE_NUM) uniqueness
dup_count = df.duplicated(subset=["CLM_ID", "LINE_NUM"]).sum()
# Result: 0 duplicates
```

#### 2.2 Financial Logic Validation
**Purpose**: Ensure financial data follows expected relationships

**Rules**:
- Submitted Charges ≥ Allowed Amount
- Allowed Amount ≥ NCH Paid Amount
- NCH Paid ≥ Provider Paid Amount

```python
df["FIN_LOGIC_VIOLATION"] = (
    (df["LINE_SBMTD_CHRG_AMT"] < df["LINE_ALOWD_CHRG_AMT"]) |
    (df["LINE_ALOWD_CHRG_AMT"] < df["LINE_NCH_PMT_AMT"]) |
    (df["LINE_NCH_PMT_AMT"] < df["LINE_PRVDR_PMT_AMT"])
)
# Result: 99.86% pass rate, 0.14% violations excluded
```

#### 2.3 Date Validation
**Purpose**: Ensure temporal consistency

**Rules**:
- Service date ≤ Processing date
- All dates within valid range

```python
df["DATE_LOGIC_VIOLATION"] = (
    df["NCH_WKLY_PROC_DT"] < df["LINE_1ST_EXPNS_DT"]
)
# Result: 100% pass rate
```

#### 2.4 Data Type Conversion
```python
# Convert financial columns to float
financial_cols = ["LINE_SBMTD_CHRG_AMT", "LINE_ALOWD_CHRG_AMT", 
                  "LINE_NCH_PMT_AMT", "LINE_PRVDR_PMT_AMT"]
for col in financial_cols:
    df[col] = df[col].astype(float)

# Convert date columns
date_cols = ["LINE_1ST_EXPNS_DT", "NCH_WKLY_PROC_DT"]
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")
```

#### 2.5 Temporal Filtering
**Focus**: 2022 data only for consistency
```python
df["SERVICE_YEAR"] = df["LINE_1ST_EXPNS_DT"].dt.year
df_2022 = df[df["SERVICE_YEAR"] == 2022].copy()
# Result: 174,645 records
```

**Final Clean Dataset**: 174,411 claim lines (99.87% of 2022 data)

---

## Analytical Framework

### Stage 3: Revenue Realization Analysis

#### 3.1 Core Metrics

**Underpayment Amount**:
```python
UNDERPAYMENT_AMT = LINE_ALOWD_CHRG_AMT - LINE_NCH_PMT_AMT
```

**Realization Rate** (primary KPI):
```python
REALIZATION_RATE = (LINE_NCH_PMT_AMT / LINE_ALOWD_CHRG_AMT) × 100
```

**Collection Efficiency**:
```python
NET_COLLECTION_RATE = LINE_PRVDR_PMT_AMT / LINE_ALOWD_CHRG_AMT
```

**Denial Rate**:
```python
DENIAL_RATE = 1 - REALIZATION_RATE = (UNDERPAYMENT_AMT / LINE_ALOWD_CHRG_AMT)
```

**Gross-to-Net Ratio**:
```python
GROSS_TO_NET = LINE_PRVDR_PMT_AMT / LINE_SBMTD_CHRG_AMT
```

#### 3.2 Processing Delay Calculation
```python
PROCESSING_DELAY_DAYS = (NCH_WKLY_PROC_DT - LINE_1ST_EXPNS_DT).days
```
**Range**: 1-8 days (reflects Medicare efficiency)

---

### Stage 4: Payment Pattern Classification

#### 4.1 Payment Status Categories

**Zero-Paid** (Denial Proxy):
```python
ZERO_PAID_FLAG = (LINE_NCH_PMT_AMT == 0)
# Result: 61.0% of claims
```

**Partial-Paid** (Adjustment/Reduction):
```python
PARTIAL_PAID_FLAG = (
    (LINE_NCH_PMT_AMT > 0) & 
    (LINE_NCH_PMT_AMT < LINE_ALOWD_CHRG_AMT)
)
# Result: 33.4% of claims
```

**Fully-Paid** (Normal Processing):
```python
FULLY_PAID_FLAG = np.isclose(
    LINE_NCH_PMT_AMT, 
    LINE_ALOWD_CHRG_AMT, 
    atol=1  # $1 tolerance for rounding
)
# Result: 6.3% of claims
```

#### 4.2 Leakage Attribution
- Zero-Paid Leakage: $1.37M (25% of total)
- Partial-Paid Leakage: $4.11M (75% of total)

**Insight**: Focus on partial payment recovery, not just denial prevention

---

### Stage 5: HCPCS-Level Analysis

#### 5.1 Aggregation by Procedure Code

```python
hcpcs_summary = df.groupby("HCPCS_CD").agg({
    "LINE_NUM": "count",                      # Volume
    "LINE_ALOWD_CHRG_AMT": "sum",            # Revenue
    "LINE_NCH_PMT_AMT": "sum",               # Payments
    "UNDERPAYMENT_AMT": "sum",               # Leakage
    "PROCESSING_DELAY_DAYS": "sum"           # Total delays
})

hcpcs_summary["realization_rate"] = (
    hcpcs_summary["paid_amt"] / hcpcs_summary["allowed_amt"]
)
```

#### 5.2 Pareto Analysis (80/20 Rule)

**Method**: Cumulative underpayment percentage
```python
hcpcs_summary = hcpcs_summary.sort_values("underpayment_amt", ascending=False)
hcpcs_summary["cum_underpayment_pct"] = (
    hcpcs_summary["underpayment_amt"].cumsum() / 
    hcpcs_summary["underpayment_amt"].sum()
)

# Identify codes contributing to 80% of leakage
pareto_80 = hcpcs_summary[hcpcs_summary["cum_underpayment_pct"] <= 0.8]
```

**Finding**: 2 codes account for 42% of all underpayment

---

### Stage 6: Specialty-Level Analysis

```python
specialty_summary = df.groupby("PRVDR_SPCLTY").agg({
    "LINE_ALOWD_CHRG_AMT": "sum",
    "LINE_NCH_PMT_AMT": "sum",
    "UNDERPAYMENT_AMT": "sum",
    "PROCESSING_DELAY_DAYS": "sum"
})

specialty_summary["realization_rate"] = (
    specialty_summary["paid_amt"] / specialty_summary["allowed_amt"]
)
```

**Finding**: Specialty 01 has 24.2% denial rate vs 22.2% average

---

### Stage 7: Risk Identification

#### 7.1 Statistical Outlier Detection

**Method**: Interquartile Range (IQR)

**Underpayment Outliers**:
```python
Q1 = hcpcs_summary["mean_underpay_pct"].quantile(0.25)
Q3 = hcpcs_summary["mean_underpay_pct"].quantile(0.75)
IQR = Q3 - Q1

OUTLIER_THRESHOLD = Q3 + 1.5 × IQR

hcpcs_summary["UNDERPAY_OUTLIER"] = (
    mean_underpay_pct > OUTLIER_THRESHOLD
)
```

**Delay Outliers**: Same method applied to processing delay

#### 7.2 Variation Analysis

**Coefficient of Variation (CV)**:
```python
CV_underpay = std_underpay_pct / mean_underpay_pct
CV_delay = std_delay_days / mean_delay_days
```

**Interpretation**:
- Low CV (<0.5): Stable, predictable process
- High CV (>1.0): Unstable, inconsistent outcomes

#### 7.3 High-Risk Service Flagging

**Criteria** (any one triggers flag):
1. Underpayment outlier (>90th percentile)
2. Delay outlier (>90th percentile)
3. Realization rate <90%
4. High variation (CV >90th percentile)

```python
hcpcs_summary["HIGH_RISK_FLAG"] = (
    (UNDERPAY_OUTLIER) |
    (DELAY_OUTLIER) |
    (realization_rate < 0.9) |
    (cv_underpay > cv_underpay.quantile(0.9)) |
    (cv_delay > cv_delay.quantile(0.9))
)
```

**Result**: 12 high-risk services identified

---

### Stage 8: AR Aging Analysis

#### 8.1 Bucket Creation

```python
bins = [-1, 30, 60, 90, 180, np.inf]
labels = ["0-30", "31-60", "61-90", "91-180", ">180"]

df["AR_BUCKET"] = pd.cut(
    df["PROCESSING_DELAY_DAYS"], 
    bins=bins, 
    labels=labels
)
```

**Limitation**: All claims fall in 0-30 day bucket due to Medicare efficiency
- Traditional AR aging not applicable
- Pivot to underpayment and payment status analysis instead

---

### Stage 9: Denial Code Analysis

```python
denial_summary = df[df["CARR_CLM_PMT_DNL_CD"].notna()].groupby(
    "CARR_CLM_PMT_DNL_CD"
).agg({
    "CLM_ID": "count",
    "UNDERPAYMENT_AMT": "sum",
    "LINE_ALOWD_CHRG_AMT": "sum"
})
```

**Finding**: Denial code "1" dominates (174,411 instances)
- Further investigation shows concentration in specific procedures
- Top diagnoses: Z733, Z608, T7432X

---

## Output Generation

### Deliverables

1. **Excel Workbook** (RCM_Analysis_Final.xlsx):
   - Executive Summary
   - Top Opportunities (with recovery estimates)
   - Overall Metrics
   - HCPCS Analysis (top 20)
   - Specialty Analysis
   - Leakage Breakdown

2. **CSV Outputs**:
   - hcpcs_underpayment_summary.csv
   - specialty_realization_summary.csv
   - hcpcs_denial_proxy_summary.csv
   - hcpcs_delay_summary.csv
   - hcpcs_variation_outliers.csv
   - high_risk_services.csv

3. **Visualizations**:
   - Revenue waterfall
   - Pareto chart (top leakage drivers)
   - Payment distribution
   - Underpayment severity histogram
   - AR aging (limited by data)
   - Delay patterns
   - Variation scatter plots

---

## Quality Assurance

### Data Validation Checkpoints

✓ **Uniqueness**: 0 duplicate (CLM_ID, LINE_NUM)  
✓ **Financial Logic**: 99.86% pass rate  
✓ **Date Logic**: 100% pass rate  
✓ **Missing Values**: 0% in critical financial fields  
✓ **Data Type Consistency**: All conversions successful  

### Analytical Validation

✓ **Metric Consistency**: All derived metrics mathematically correct  
✓ **Aggregation Accuracy**: Totals reconcile across dimensions  
✓ **Outlier Detection**: IQR method appropriately identifies extremes  
✓ **Pareto Validation**: Cumulative percentages sum to 100%  

---

## Assumptions & Limitations

### Assumptions

1. **Submitted = Allowed**: In this dataset, they're identical (0% discount rate)
   - Real-world typically has 20-40% contractual adjustments
   
2. **Zero-Paid = Denial**: Payment of $0 used as denial proxy
   - Actual denial codes limited in synthetic data
   
3. **20% Recovery Rate**: Conservative estimate for potential recovery
   - Industry benchmarks: 15-30% of denials/underpayments recoverable

### Limitations

1. **Synthetic Data**: May not reflect all real-world complexity
   - Simplified payer behavior
   - Limited denial reason codes
   - Standardized processing times

2. **Medicare Only**: No commercial payer mix
   - Different reimbursement rates
   - Varied authorization requirements
   - Different denial patterns

3. **Processing Times**: 4-day average vs typical 30-90 days
   - Prevents traditional AR aging analysis
   - Masks cash flow issues

4. **Temporal Scope**: 2022 data only
   - No trend analysis over years
   - Cannot assess seasonal patterns

---

## Reproducibility

### Environment

- Python 3.8+
- pandas 1.5+
- numpy 1.23+
- matplotlib 3.6+
- seaborn 0.12+

### Execution

1. Place carrier claims CSV in `data/raw/`
2. Run `python src/rcm_analysis.py`
3. Outputs generated in `data/outputs/` and `results/`

### Expected Runtime

- Data cleaning: ~2-3 minutes
- Analysis: ~5-7 minutes
- Visualization: ~2-3 minutes
- **Total**: ~10-15 minutes (for 174K records)

---

## References

### Industry Benchmarks

- **HFMA**: Healthcare Financial Management Association
  - Realization Rate Benchmark: 95-98%
  - Days in AR: 30-40 days industry average

- **MGMA**: Medical Group Management Association
  - Clean Claim Rate: 90-95%
  - Denial Rate: 5-10%

### CMS Resources

- SynPUF Documentation: [CMS.gov](https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs)
- Claims Data Dictionary: Available in SynPUF documentation
- ICD/CPT/HCPCS Code Sets: [cms.gov/medicare/coding](https://www.cms.gov/medicare/coding)

---

*Last Updated: January 2025*