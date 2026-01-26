"""
Medicare Revenue Cycle Management Analysis
Main analysis script - orchestrates the complete RCM analysis pipeline

Author: [Your Name]
Date: January 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

class RCMAnalyzer:
    """
    Main class for Revenue Cycle Management analysis
    """
    
    def __init__(self, data_path):
        """
        Initialize analyzer with data path
        
        Parameters:
        -----------
        data_path : str
            Path to carrier claims CSV file
        """
        self.data_path = data_path
        self.df = None
        self.df_clean = None
        self.results = {}
        
    def load_data(self):
        """Load and perform initial data setup"""
        print("Loading data...")
        
        # Read raw data
        self.df = pd.read_csv(self.data_path, header=None, low_memory=False)
        
        # Set column names from second row
        self.df.columns = self.df.iloc[1]
        
        # Drop metadata rows
        self.df = self.df.drop([0, 1]).reset_index(drop=True)
        
        print(f"✓ Loaded {len(self.df):,} records with {len(self.df.columns)} columns")
        
    def clean_data(self):
        """Data cleaning and validation pipeline"""
        print("\nCleaning and validating data...")
        
        # 1. Check for duplicates
        dup_count = self.df.duplicated(subset=["CLM_ID", "LINE_NUM"]).sum()
        print(f"  - Duplicates found: {dup_count}")
        
        # 2. Convert financial columns to float
        financial_cols = [
            "LINE_SBMTD_CHRG_AMT",
            "LINE_ALOWD_CHRG_AMT",
            "LINE_NCH_PMT_AMT",
            "LINE_PRVDR_PMT_AMT"
        ]
        
        for col in financial_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # 3. Convert date columns
        date_cols = ["LINE_1ST_EXPNS_DT", "NCH_WKLY_PROC_DT"]
        for col in date_cols:
            self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
        
        # 4. Financial logic validation
        self.df["FIN_LOGIC_VIOLATION"] = (
            (self.df["LINE_SBMTD_CHRG_AMT"] < self.df["LINE_ALOWD_CHRG_AMT"]) |
            (self.df["LINE_ALOWD_CHRG_AMT"] < self.df["LINE_NCH_PMT_AMT"]) |
            (self.df["LINE_NCH_PMT_AMT"] < self.df["LINE_PRVDR_PMT_AMT"])
        )
        
        violations = self.df["FIN_LOGIC_VIOLATION"].sum()
        print(f"  - Financial logic violations: {violations} ({100*violations/len(self.df):.2f}%)")
        
        # 5. Date logic validation
        self.df["DATE_LOGIC_VIOLATION"] = (
            self.df["NCH_WKLY_PROC_DT"] < self.df["LINE_1ST_EXPNS_DT"]
        )
        
        # 6. Filter to 2022 data
        self.df["SERVICE_YEAR"] = self.df["LINE_1ST_EXPNS_DT"].dt.year
        df_2022 = self.df[self.df["SERVICE_YEAR"] == 2022].copy()
        print(f"  - 2022 records: {len(df_2022):,}")
        
        # 7. Create clean dataset (exclude violations)
        self.df_clean = df_2022[df_2022["FIN_LOGIC_VIOLATION"] == False].copy()
        
        excluded_pct = 100 * (1 - len(self.df_clean) / len(df_2022))
        print(f"  - Clean dataset: {len(self.df_clean):,} records ({excluded_pct:.2f}% excluded)")
        print("✓ Data cleaning complete")
        
    def calculate_metrics(self):
        """Calculate core RCM metrics"""
        print("\nCalculating revenue metrics...")
        
        df = self.df_clean
        
        # Processing delay
        df["PROCESSING_DELAY_DAYS"] = (
            df["NCH_WKLY_PROC_DT"] - df["LINE_1ST_EXPNS_DT"]
        ).dt.days
        
        # Underpayment
        df["UNDERPAYMENT_AMT"] = (
            df["LINE_ALOWD_CHRG_AMT"] - df["LINE_NCH_PMT_AMT"]
        )
        
        # Realization rate
        df["REALIZATION_RATE"] = (
            df["LINE_NCH_PMT_AMT"] / df["LINE_ALOWD_CHRG_AMT"]
        )
        
        # Payment classifications
        df["ZERO_PAID_FLAG"] = df["LINE_NCH_PMT_AMT"] == 0
        df["PARTIAL_PAID_FLAG"] = (
            (df["LINE_NCH_PMT_AMT"] > 0) &
            (df["LINE_NCH_PMT_AMT"] < df["LINE_ALOWD_CHRG_AMT"])
        )
        df["FULLY_PAID_FLAG"] = np.isclose(
            df["LINE_NCH_PMT_AMT"],
            df["LINE_ALOWD_CHRG_AMT"],
            atol=1
        )
        
        self.df_clean = df
        
        # Calculate summary metrics
        self.results['overall'] = {
            'total_claims': len(df),
            'total_revenue': df["LINE_ALOWD_CHRG_AMT"].sum(),
            'total_paid': df["LINE_NCH_PMT_AMT"].sum(),
            'total_leakage': df["UNDERPAYMENT_AMT"].sum(),
            'realization_rate': 100 * df["LINE_NCH_PMT_AMT"].sum() / df["LINE_ALOWD_CHRG_AMT"].sum(),
            'zero_paid_pct': 100 * df["ZERO_PAID_FLAG"].mean(),
            'partial_paid_pct': 100 * df["PARTIAL_PAID_FLAG"].mean(),
            'avg_delay': df["PROCESSING_DELAY_DAYS"].mean()
        }
        
        print("✓ Metrics calculated")
        
    def analyze_hcpcs(self):
        """HCPCS-level analysis and Pareto"""
        print("\nAnalyzing HCPCS codes...")
        
        df = self.df_clean
        
        hcpcs_summary = df.groupby("HCPCS_CD", as_index=False).agg({
            "LINE_NUM": "count",
            "LINE_ALOWD_CHRG_AMT": "sum",
            "LINE_NCH_PMT_AMT": "sum",
            "UNDERPAYMENT_AMT": "sum",
            "PROCESSING_DELAY_DAYS": "sum"
        }).rename(columns={
            "LINE_NUM": "services",
            "LINE_ALOWD_CHRG_AMT": "allowed_amt",
            "LINE_NCH_PMT_AMT": "paid_amt",
            "UNDERPAYMENT_AMT": "underpayment_amt",
            "PROCESSING_DELAY_DAYS": "total_delays"
        })
        
        hcpcs_summary["realization_rate"] = (
            hcpcs_summary["paid_amt"] / hcpcs_summary["allowed_amt"]
        )
        
        # Sort by underpayment and calculate Pareto
        hcpcs_summary = hcpcs_summary.sort_values("underpayment_amt", ascending=False)
        hcpcs_summary["cum_underpayment_pct"] = (
            hcpcs_summary["underpayment_amt"].cumsum() / 
            hcpcs_summary["underpayment_amt"].sum()
        )
        
        self.results['hcpcs'] = hcpcs_summary
        
        # Identify top leakage drivers
        top_5 = hcpcs_summary.head(5)
        print(f"  - Top 5 codes account for ${top_5['underpayment_amt'].sum()/1e6:.2f}M leakage")
        print(f"  - Top 2 codes account for {100*top_5.head(2)['underpayment_amt'].sum()/hcpcs_summary['underpayment_amt'].sum():.1f}% of total")
        print("✓ HCPCS analysis complete")
        
    def analyze_specialty(self):
        """Specialty-level analysis"""
        print("\nAnalyzing specialties...")
        
        df = self.df_clean
        
        specialty_summary = df.groupby("PRVDR_SPCLTY", as_index=False).agg({
            "LINE_ALOWD_CHRG_AMT": "sum",
            "LINE_NCH_PMT_AMT": "sum",
            "UNDERPAYMENT_AMT": "sum"
        }).rename(columns={
            "LINE_ALOWD_CHRG_AMT": "allowed_amt",
            "LINE_NCH_PMT_AMT": "paid_amt",
            "UNDERPAYMENT_AMT": "underpayment_amt"
        })
        
        specialty_summary["realization_rate"] = (
            specialty_summary["paid_amt"] / specialty_summary["allowed_amt"]
        )
        
        self.results['specialty'] = specialty_summary
        print("✓ Specialty analysis complete")
        
    def identify_risks(self):
        """Identify high-risk services"""
        print("\nIdentifying high-risk services...")
        
        hcpcs_summary = self.results['hcpcs'].copy()
        
        # Flag high-risk based on multiple criteria
        hcpcs_summary["HIGH_RISK_FLAG"] = (
            (hcpcs_summary["underpayment_amt"] > hcpcs_summary["underpayment_amt"].quantile(0.9)) |
            (hcpcs_summary["realization_rate"] < 0.9)
        )
        
        high_risk = hcpcs_summary[hcpcs_summary["HIGH_RISK_FLAG"]]
        self.results['high_risk'] = high_risk
        
        print(f"  - {len(high_risk)} high-risk services identified")
        print("✓ Risk identification complete")
        
    def export_results(self, output_dir='results'):
        """Export analysis results"""
        print("\nExporting results...")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create Excel workbook
        with pd.ExcelWriter(f'{output_dir}/RCM_Analysis_Final.xlsx', engine='openpyxl') as writer:
            # Executive summary
            exec_summary = pd.DataFrame({
                'Metric': [
                    'Total Claims Analyzed',
                    'Total Revenue Processed',
                    'Revenue Realization Rate',
                    'Total Revenue Leakage',
                    'Zero-Paid Rate',
                    'Partial-Paid Rate',
                    'Avg Processing Time',
                    'High-Risk Services'
                ],
                'Value': [
                    f"{self.results['overall']['total_claims']:,}",
                    f"${self.results['overall']['total_revenue']/1e6:.2f}M",
                    f"{self.results['overall']['realization_rate']:.1f}%",
                    f"${self.results['overall']['total_leakage']/1e6:.2f}M",
                    f"{self.results['overall']['zero_paid_pct']:.1f}%",
                    f"{self.results['overall']['partial_paid_pct']:.1f}%",
                    f"{self.results['overall']['avg_delay']:.1f} days",
                    f"{len(self.results['high_risk'])}"
                ]
            })
            exec_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # Top opportunities
            top_5 = self.results['hcpcs'].head(5)[['HCPCS_CD', 'services', 'underpayment_amt', 'realization_rate']].copy()
            top_5['potential_recovery'] = top_5['underpayment_amt'] * 0.20
            top_5.to_excel(writer, sheet_name='Top_Opportunities', index=False)
            
            # HCPCS analysis
            self.results['hcpcs'].head(20).to_excel(writer, sheet_name='HCPCS_Analysis', index=False)
            
            # Specialty analysis
            self.results['specialty'].to_excel(writer, sheet_name='Specialty_Analysis', index=False)
            
            # High-risk services
            self.results['high_risk'].to_excel(writer, sheet_name='High_Risk_Services', index=False)
        
        print(f"✓ Excel workbook saved to {output_dir}/RCM_Analysis_Final.xlsx")
        
        # Export CSVs
        self.results['hcpcs'].to_csv(f'{output_dir}/hcpcs_summary.csv', index=False)
        self.results['specialty'].to_csv(f'{output_dir}/specialty_summary.csv', index=False)
        self.results['high_risk'].to_csv(f'{output_dir}/high_risk_services.csv', index=False)
        
        print(f"✓ CSV files saved to {output_dir}/")
        
    def generate_visualizations(self, output_dir='results/figures'):
        """Generate key visualizations"""
        print("\nGenerating visualizations...")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        df = self.df_clean
        
        # 1. Revenue waterfall
        plt.figure(figsize=(10, 6))
        values = [
            df["LINE_SBMTD_CHRG_AMT"].sum()/1e6,
            df["LINE_ALOWD_CHRG_AMT"].sum()/1e6,
            df["LINE_NCH_PMT_AMT"].sum()/1e6
        ]
        plt.bar(['Submitted', 'Allowed', 'Paid'], values, color=['#3498db', '#2ecc71', '#e74c3c'])
        plt.title('Revenue Flow: Submitted → Allowed → Paid', fontsize=14, fontweight='bold')
        plt.ylabel('Amount ($M)', fontsize=12)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/revenue_waterfall.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Pareto chart
        top_10 = self.results['hcpcs'].head(10)
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(top_10)), top_10['underpayment_amt']/1e6)
        plt.xticks(range(len(top_10)), top_10['HCPCS_CD'], rotation=45, ha='right')
        plt.title('Top 10 HCPCS Codes by Underpayment', fontsize=14, fontweight='bold')
        plt.ylabel('Underpayment ($M)', fontsize=12)
        plt.xlabel('HCPCS Code', fontsize=12)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/pareto_hcpcs.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Payment distribution
        zero_paid = df.loc[df["ZERO_PAID_FLAG"], "UNDERPAYMENT_AMT"].sum()/1e6
        partial_paid = df.loc[df["PARTIAL_PAID_FLAG"], "UNDERPAYMENT_AMT"].sum()/1e6
        
        plt.figure(figsize=(10, 6))
        plt.bar(['Zero-Paid', 'Partial-Paid'], [zero_paid, partial_paid], 
                color=['#e74c3c', '#f39c12'])
        plt.title('Leakage by Payment Status', fontsize=14, fontweight='bold')
        plt.ylabel('Underpayment ($M)', fontsize=12)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/payment_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Visualizations saved to {output_dir}/")
        
    def print_summary(self):
        """Print executive summary to console"""
        print("\n" + "="*60)
        print("EXECUTIVE SUMMARY")
        print("="*60)
        
        r = self.results['overall']
        
        print(f"\n📊 Dataset Overview")
        print(f"  Claims Analyzed:      {r['total_claims']:,}")
        print(f"  Revenue Processed:    ${r['total_revenue']/1e6:.2f}M")
        
        print(f"\n💰 Revenue Performance")
        print(f"  Realization Rate:     {r['realization_rate']:.1f}%")
        print(f"  Revenue Leakage:      ${r['total_leakage']/1e6:.2f}M ({100*r['total_leakage']/r['total_revenue']:.1f}%)")
        print(f"  Zero-Paid Claims:     {r['zero_paid_pct']:.1f}%")
        print(f"  Partial-Paid Claims:  {r['partial_paid_pct']:.1f}%")
        
        print(f"\n⚡ Process Efficiency")
        print(f"  Avg Processing Time:  {r['avg_delay']:.1f} days")
        print(f"  High-Risk Services:   {len(self.results['high_risk'])}")
        
        print(f"\n🎯 Top Opportunities")
        top_2 = self.results['hcpcs'].head(2)
        print(f"  Top 2 HCPCS Codes:    {', '.join(top_2['HCPCS_CD'].values)}")
        print(f"  Combined Leakage:     ${top_2['underpayment_amt'].sum()/1e6:.2f}M")
        print(f"  Share of Total:       {100*top_2['underpayment_amt'].sum()/r['total_leakage']:.1f}%")
        
        recovery = r['total_leakage'] * 0.175  # 17.5% midpoint
        print(f"\n💡 Estimated Recovery Potential")
        print(f"  Conservative (15%):   ${r['total_leakage']*0.15/1e6:.2f}M")
        print(f"  Target (17.5%):       ${recovery/1e6:.2f}M")
        print(f"  Optimistic (20%):     ${r['total_leakage']*0.20/1e6:.2f}M")
        
        print("\n" + "="*60)
        
    def run_full_analysis(self):
        """Execute complete analysis pipeline"""
        print("\n" + "="*60)
        print("MEDICARE REVENUE CYCLE MANAGEMENT ANALYSIS")
        print("="*60)
        
        self.load_data()
        self.clean_data()
        self.calculate_metrics()
        self.analyze_hcpcs()
        self.analyze_specialty()
        self.identify_risks()
        self.export_results()
        self.generate_visualizations()
        self.print_summary()
        
        print("\n✅ Analysis complete!")
        print("="*60 + "\n")


def main():
    """Main execution function"""
    
    # Configuration
    DATA_PATH = "data/raw/carrier01.csv"
    
    # Initialize analyzer
    analyzer = RCMAnalyzer(DATA_PATH)
    
    # Run analysis
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()