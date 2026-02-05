# Medicare Revenue Cycle Operations (ROS) Analysis

## Project Overview

A comprehensive data analytics project examining Medicare Part B (Carrier) claims to identify revenue cycle inefficiencies, payment delays, and systematic underpayment patterns. This analysis transforms $5.48M in revenue leakage into actionable operational intelligence with $575K-$625K recovery potential.

**Key Achievement**: Identified that 57% of revenue leakage stems from behavioral health services with systematic coverage limitations, enabling targeted interventions.

---

## Business Impact

| Metric | Value | Impact |
|--------|-------|--------|
| **Revenue Leakage Identified** | $5.48M (22.2% of allowed charges) | Quantified operational inefficiency |
| **Claims Analyzed** | 174,411 line-level transactions | Comprehensive coverage |
| **Recovery Opportunity** | $575K-$625K annually | 10.5-11.4% reduction in leakage |
| **High-Risk Services Flagged** | 12 HCPCS codes | Targeted intervention points |
| **Root Causes Identified** | 8 distinct dimensions | Systematic, addressable patterns |

---

## Key Findings

### 1. **Pareto Concentration**
- Top 2 HCPCS codes (96156, 94010) account for **42% of total underpayment**
- Behavioral health services (Z-codes) drive **57% of revenue leakage**

### 2. **The Behavioral Health Hypothesis**
```
HCPCS 96156 (Health Behavior Assessment) + Diagnosis Z733 (Stress)
    ↓
61% denial rate in Office settings (POS 11)
    ↓
$1.66M in underpayment from stress-related counseling alone
```

### 3. **The Complexity Paradox**
- **1 diagnosis**: 18% denial rate ✓
- **4+ diagnoses**: 60-65% denial rate ✗
- **Finding**: More documentation correlates with MORE denials (counterintuitive)

### 4. **Geographic Variation**
- Denial rates range from 56% (low) to 67% (Connecticut) across states
- Root cause: Regional Medicare Administrative Contractor (MAC) policies

### 5. **Payment Pattern Analysis**
- **75% of leakage**: Partial payments (adjustments)
- **25% of leakage**: Zero payments (denials)
- **Implication**: Focus on improving partial payment rates for maximum impact

---

## Technologies Used

| Category | Tools |
|----------|-------|
| **Programming** | Python 3.x |
| **Data Analysis** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |
| **Environment** | Google Colab |
| **Data Format** | CSV, XLSX |
| **Documentation** | Markdown, Word (python-docx) |

---



---

## Methodology

### **6-Step ROS Framework**

| Step | Focus Area | Key Output |
|------|-----------|------------|
| **C1** | Data Validation | Quality checks, 99.86% pass rate |
| **C2** | Revenue Realization | $5.48M underpayment identified |
| **C3** | Denial Proxy Analysis | 61% zero-paid, 33.4% partial-paid |
| **C4** | Delay & AR Analysis | 4-day avg processing (excellent) |
| **C5** | Variation Analysis | Stability metrics, CV analysis |
| **C6** | Outlier Detection | 12 high-risk services flagged |

### **8-Dimension Root Cause Analysis**

1. **Diagnosis Patterns** → Behavioral health codes show 70%+ denial rates
2. **Place of Service** → Office (POS 11) has 62% denial vs. 11% in hospitals
3. **Provider Characteristics** → State-level variation (56-67% denial range)
4. **Service Complexity** → 12 diagnoses = 75% of dataset at 60% denial
5. **Temporal Patterns** → Consistent across months, slight day-of-week variation
6. **Carrier Patterns** → MAC-specific policies drive geographic differences
7. **Procedure Modifiers** → Limited impact (insufficient data)
8. **Assignment Status** → All claims assigned (homogeneous)

---

## Key Metrics & Formulas

### Revenue Cycle Metrics

# Underpayment Amount
underpayment = allowed_amount - paid_amount

# Revenue Realization Rate
realization_rate = (paid_amount / allowed_amount) * 100

# Denial Rate
denial_rate = 1 - (paid_amount / allowed_amount)

# Processing Delay (AR Proxy)
delay_days = processing_date - service_date

# Zero-Paid Flag (Denial Proxy)
zero_paid = (paid_amount == 0)

# Partial-Paid Flag
partial_paid = (paid_amount > 0) & (paid_amount < allowed_amount)
```

### Statistical Metrics

```
# Coefficient of Variation (Stability)
CV = standard_deviation / mean

# IQR Outlier Detection
outlier = value > Q3 + 1.5 * IQR

# Pareto Analysis
cumulative_percent = cumulative_sum / total_sum
```

---

### Run Basic Analysis
```python
# Load and validate data
df = pd.read_csv('carrier01.csv')

# Filter to 2022
df_2022 = df[df['SERVICE_YEAR'] == 2022]

# Calculate underpayment
df_2022['UNDERPAYMENT_AMT'] = (
    df_2022['LINE_ALOWD_CHRG_AMT'] - df_2022['LINE_NCH_PMT_AMT']
)

# Aggregate by HCPCS
hcpcs_summary = df_2022.groupby('HCPCS_CD').agg({
    'LINE_NUM': 'count',
    'LINE_ALOWD_CHRG_AMT': 'sum',
    'LINE_NCH_PMT_AMT': 'sum',
    'UNDERPAYMENT_AMT': 'sum'
})

# Calculate realization rate
hcpcs_summary['realization_rate'] = (
    hcpcs_summary['LINE_NCH_PMT_AMT'] / 
    hcpcs_summary['LINE_ALOWD_CHRG_AMT']
)
```

### Run Root Cause Analysis
```python
# Diagnosis pattern analysis
diagnosis_leakage = df_2022.groupby('PRNCPAL_DGNS_CD').agg({
    'CLM_ID': 'count',
    'UNDERPAYMENT_AMT': ['sum', 'mean'],
    'ZERO_PAID_FLAG': 'mean'
})

# Place of service analysis
pos_performance = df_2022.groupby('LINE_PLACE_OF_SRVC_CD').agg({
    'CLM_ID': 'count',
    'ZERO_PAID_FLAG': 'mean',
    'UNDERPAYMENT_AMT': 'mean'
})

# Complexity analysis
df_2022['NUM_DIAGNOSES'] = df_2022[diagnosis_cols].notna().sum(axis=1)
complexity_impact = df_2022.groupby('NUM_DIAGNOSES').agg({
    'ZERO_PAID_FLAG': 'mean',
    'UNDERPAYMENT_AMT': 'mean'
})
```

---

## Sample Visualizations

### Revenue Waterfall
![Revenue Flow](figures/1_revenue_waterfall.png)

### Pareto Analysis - Top 10 HCPCS
![Pareto](figures/2_pareto_top10_hcpcs.png)

### Leakage Breakdown
![Leakage](figures/3_leakage_breakdown.png)

---

## Actionable Recommendations

### Phase 1: Quick Wins (0-30 Days) → $150K-$200K/month

1. **Pre-submission review** for Z-code diagnoses (stress, counseling, substance abuse)
2. **Provider education** on HCPCS 96156 coverage limitations
3. **Flag claims** with 12 diagnoses for coding optimization
4. **State-specific protocols** for high-denial regions (CT, MS, TN)

### Phase 2: Process Improvements (30-90 Days) → $200K-$300K

1. Build **automated denial prediction model** using root cause factors
2. Establish **carrier-specific submission guidelines**
3. Implement **place-of-service optimization** (shift to POS 22 where viable)
4. Create **diagnosis + HCPCS combination alerts**

### Phase 3: Strategic Initiatives (90-180 Days) → $400K-$600K annual

1. **Negotiate with Medicare MACs** on behavioral health coverage
2. Develop **alternative service delivery models** (telehealth, group sessions)
3. Implement **continuous monitoring dashboard** with root cause alerts
4. **Expand analysis** to provider-specific patterns

---

## Key Insights for Stakeholders

### For Executives
- **ROI**: $575K-$625K annual recovery opportunity (10.5-11.4% reduction in leakage)
- **Risk Concentration**: 57% of leakage from behavioral health services enables targeted action
- **Quick Wins**: Phase 1 interventions require minimal investment with immediate impact

### For Revenue Cycle Managers
- **Top Priority**: HCPCS 96156 and 94010 account for $2.29M in underpayment (42% of total)
- **Process Insight**: 75% of leakage is partial payments, not denials—focus on payment rate improvement
- **Geographic Strategy**: 11-point denial rate variance across states requires regional protocols

### For Data Teams
- **Data Quality**: 99.86% of records passed financial logic validation
- **Analytical Depth**: 8-dimension root cause framework with 35 high-risk diagnoses identified
- **Scalability**: Framework reusable for other payers, years, or service lines

---

## Data Sources

- **Source**: CMS Medicare Part B Carrier Claims Public Use File (PUF)
- **Year**: 2022 Calendar Year
- **Volume**: 174,645 claim lines after filtering
- **Columns**: 96 variables including financial, clinical, and administrative data

---

## Limitations & Caveats

1. **Single Year Scope**: Limited to 2022; cannot assess trends
2. **Denial Code Ambiguity**: All claims show code "1" - meaning unclear
3. **Missing HCPCS**: 62.2% of lines lack procedure codes
4. **Synthetic Data**: May be sampled/synthetic PUF; generalizability uncertain
5. **Correlation ≠ Causation**: Root causes inferred, not confirmed with policy documents

---

## Documentation

- [Detailed Analysis Report](reports/Medicare_Carrier_Analysis_Detailed_Report.docx) - 25 pages
- [Integrated Root Cause Analysis](reports/Integrated_Root_Cause_Analysis.docx) - 30 pages
- [Executive Summary](results/RCM_Analysis_Final.xlsx) - Dashboard workbook

---

## Author

**Abhinav Verma**  
Data Analyst | Healthcare Revenue Cycle  
[LinkedIn](www.linkedin.com/in/abhinavverma-mph-ha)
---

## License

This project is for educational and portfolio purposes. Data used is from publicly available CMS files.

---

## Acknowledgments

- CMS for providing public use files
- Medicare Administrative Contractors (MACs) documentation
- Revenue Cycle Operations best practices framework

---

## Contact

For questions or collaboration opportunities:
- Email: abhinav.ha01@gmail.com
- LinkedIn: [www.linkedin.com/in/abhinavverma-mph-ha)

---

## Future Enhancements

- [ ] Multi-year trend analysis (2020-2024)
- [ ] Provider-level performance benchmarking
- [ ] Machine learning denial prediction model
- [ ] Interactive Power BI/Tableau dashboard
- [ ] Integration with claims management system APIs
- [ ] Real-time monitoring and alerting framework
- [ ] Expand to Medicare Part A (Inpatient) analysis

---

**⭐ If this project helped you, please give it a star!**
