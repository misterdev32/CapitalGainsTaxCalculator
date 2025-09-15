# Quickstart Guide: Crypto Capital Gains Tax Calculator

**Date**: 2025-01-15  
**Feature**: 001-a-personalized-version  
**Status**: Complete

## Overview

This quickstart guide demonstrates the complete workflow for using the Crypto Capital Gains Tax Calculator to aggregate transactions, calculate Irish CGT obligations, and generate audit-proof reports.

## Prerequisites

- Python 3.11+ installed
- Binance API credentials (read-only)
- CSV exports from Revolut and other exchanges
- Basic understanding of Irish Capital Gains Tax rules

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/crypto-tax-calculator.git
cd crypto-tax-calculator

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m crypto_tax_calculator.cli.main init-db
```

## Step 1: Configure Exchanges

### Binance API Setup
```bash
# Set up Binance API credentials
python -m crypto_tax_calculator.cli.main configure-exchange \
  --exchange binance \
  --api-key YOUR_API_KEY \
  --api-secret YOUR_API_SECRET
```

### CSV Exchange Setup
```bash
# Configure CSV-based exchanges
python -m crypto_tax_calculator.cli.main configure-exchange \
  --exchange revolut \
  --type csv
```

## Step 2: Import Transaction Data

### Sync Binance Data
```bash
# Sync all historical data from Binance
python -m crypto_tax_calculator.cli.main sync-binance \
  --start-date 2021-01-01 \
  --end-date 2024-12-31 \
  --exchange-types spot futures margin fiat
```

### Import CSV Data
```bash
# Import Revolut CSV
python -m crypto_tax_calculator.cli.main import-csv \
  --file revolut_transactions.csv \
  --exchange revolut

# Import other exchange CSVs
python -m crypto_tax_calculator.cli.main import-csv \
  --file coinbase_transactions.csv \
  --exchange coinbase
```

## Step 3: Calculate CGT

### Generate Tax Year Report
```bash
# Calculate CGT for 2024 tax year
python -m crypto_tax_calculator.cli.main calculate-cgt \
  --tax-year 2024 \
  --force-recalculate
```

### View Report Summary
```bash
# Get CGT summary
python -m crypto_tax_calculator.cli.main get-cgt-summary \
  --tax-year 2024
```

## Step 4: Export Reports

### Export for ROS Filing
```bash
# Export CGT report for ROS
python -m crypto_tax_calculator.cli.main export-cgt \
  --tax-year 2024 \
  --format excel \
  --include-transactions \
  --output-file cgt_report_2024.xlsx
```

### Export Audit Trail
```bash
# Export detailed audit trail
python -m crypto_tax_calculator.cli.main export-audit \
  --tax-year 2024 \
  --format csv \
  --output-file audit_trail_2024.csv
```

## Step 5: Launch Web Dashboard

```bash
# Start the web dashboard
python -m crypto_tax_web.cli.main start-dashboard \
  --port 8501 \
  --host localhost
```

Open your browser to `http://localhost:8501` to view:
- Portfolio overview
- Transaction history
- CGT calculations
- Data visualizations
- Export options

## Validation Scenarios

### Scenario 1: Complete Data Import
**Given**: Fresh installation with no data
**When**: User imports all transaction sources
**Then**: System should show:
- Total transactions imported
- Data source breakdown
- Validation warnings/errors
- Data quality score

### Scenario 2: CGT Calculation
**Given**: Complete transaction data for 2024
**When**: User calculates CGT for 2024
**Then**: System should show:
- Total realized gains: €X,XXX
- Total realized losses: €X,XXX
- Net gains: €X,XXX
- Exemption applied: €1,270
- Tax due: €X,XXX (33% of taxable gains)

### Scenario 3: Data Reconciliation
**Given**: Data from both API and CSV sources
**When**: User runs data reconciliation
**Then**: System should show:
- Matched transactions
- Discrepancies found
- Data quality metrics
- Recommendations for resolution

### Scenario 4: Report Export
**Given**: Calculated CGT report
**When**: User exports report for ROS
**Then**: System should generate:
- Excel file with CGT summary
- Detailed transaction breakdown
- Audit trail documentation
- ROS-compatible format

## Troubleshooting

### Common Issues

1. **Binance API Rate Limits**
   ```bash
   # Check rate limit status
   python -m crypto_tax_calculator.cli.main check-rate-limits
   
   # Resume sync with rate limiting
   python -m crypto_tax_calculator.cli.main sync-binance --resume
   ```

2. **CSV Import Errors**
   ```bash
   # Validate CSV before import
   python -m crypto_tax_calculator.cli.main validate-csv \
     --file transactions.csv \
     --exchange revolut
   
   # Get CSV template
   python -m crypto_tax_calculator.cli.main get-csv-template \
     --exchange revolut
   ```

3. **CGT Calculation Issues**
   ```bash
   # Check data quality
   python -m crypto_tax_calculator.cli.main check-data-quality \
     --tax-year 2024
   
   # Recalculate with debug info
   python -m crypto_tax_calculator.cli.main calculate-cgt \
     --tax-year 2024 \
     --debug \
     --force-recalculate
   ```

### Data Validation

```bash
# Run comprehensive data validation
python -m crypto_tax_calculator.cli.main validate-data \
  --check-duplicates \
  --check-missing-prices \
  --check-tax-year-assignment \
  --check-fifo-calculations
```

### Performance Optimization

```bash
# Optimize database
python -m crypto_tax_calculator.cli.main optimize-db

# Clear cache
python -m crypto_tax_calculator.cli.main clear-cache

# Rebuild indexes
python -m crypto_tax_calculator.cli.main rebuild-indexes
```

## Expected Outputs

### CGT Report (2024)
```
Tax Year: 2024
Total Gains: €15,420.50
Total Losses: €3,210.75
Net Gains: €12,209.75
Exemption Applied: €1,270.00
Taxable Gains: €10,939.75
Tax Due: €3,610.12 (33%)
Transactions: 1,247
Exchanges: binance, revolut, coinbase
```

### Data Quality Report
```
Total Transactions: 1,247
Data Sources: API (892), CSV (355)
Validation Errors: 0
Validation Warnings: 3
Data Quality Score: 98.5%
Missing Price Data: 0
Duplicate Transactions: 0
```

### Audit Trail
```
Transaction ID: tx_123456
Source: binance_api
Date: 2024-03-15 14:30:00 UTC
Asset: BTC
Action: sell
Amount: -0.5
Price EUR: €45,230.00
Cost Basis: €22,615.00
Realized Gain: €22,615.00
Tax Year: 2024
```

## Next Steps

1. **Regular Maintenance**
   - Set up automated daily sync
   - Monitor data quality
   - Update exchange configurations

2. **Advanced Features**
   - Set up real-time price updates
   - Configure automated reporting
   - Implement data backup strategies

3. **Compliance**
   - Review audit trails regularly
   - Maintain data retention policies
   - Keep exchange credentials secure

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the data model documentation
- Consult the API contracts
- Contact support@cryptotaxcalc.com
