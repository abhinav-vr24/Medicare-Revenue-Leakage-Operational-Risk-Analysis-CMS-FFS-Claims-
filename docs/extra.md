## Overview

This document details the technical methodology used in the Medicare Revenue Cycle Management (RCM) Analysis project. The analysis follows a structured, multi-stage approach to ensure data quality, analytical rigor, and actionable insights.


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