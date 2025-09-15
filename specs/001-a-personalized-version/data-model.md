# Data Model: Crypto Capital Gains Tax Calculator

**Date**: 2025-01-15  
**Feature**: 001-a-personalized-version  
**Status**: Complete

## Core Entities

### Transaction
**Purpose**: Normalized transaction record from all exchanges
**Schema**: 
```python
class Transaction:
    id: str                    # Unique identifier
    date: datetime            # Transaction timestamp (UTC)
    exchange: str             # Source exchange (binance, revolut, etc.)
    asset: str                # Cryptocurrency symbol (BTC, ETH, etc.)
    action: str               # buy, sell, swap, transfer, staking, fee
    amount: Decimal           # Quantity of asset
    price_eur: Decimal        # Price in EUR at time of transaction
    fee: Decimal              # Transaction fee in EUR
    fee_asset: str            # Asset used for fee payment
    tx_id: str                # Exchange transaction ID
    source: str               # api, csv, manual
    created_at: datetime      # Record creation timestamp
    updated_at: datetime      # Last update timestamp
    is_taxable: bool          # Whether transaction affects CGT
    tax_year: int             # Irish tax year (e.g., 2024)
    cost_basis: Decimal       # FIFO cost basis for disposal
    realized_gain_loss: Decimal # Calculated gain/loss
```

**Validation Rules**:
- `amount` must be positive for buy/swap, negative for sell
- `price_eur` must be positive
- `fee` must be non-negative
- `date` must be within reasonable range (2010-2030)
- `action` must be one of: buy, sell, swap, transfer, staking, fee
- `exchange` must be one of: binance, revolut, coinbase, kucoin, kraken

**State Transitions**:
- `created` → `validated` → `processed` → `archived`
- Failed validation → `error` state with error details

### Asset
**Purpose**: Cryptocurrency metadata and price history
**Schema**:
```python
class Asset:
    symbol: str               # Asset symbol (BTC, ETH, etc.)
    name: str                 # Full name (Bitcoin, Ethereum, etc.)
    decimals: int             # Decimal places for calculations
    is_active: bool           # Whether asset is still traded
    created_at: datetime      # First seen timestamp
    updated_at: datetime      # Last update timestamp
```

**Validation Rules**:
- `symbol` must be uppercase and 3-10 characters
- `name` must be non-empty
- `decimals` must be between 0 and 18

### CGT Report
**Purpose**: Generated tax report for specific tax year
**Schema**:
```python
class CGTReport:
    id: str                   # Report identifier
    tax_year: int             # Irish tax year
    total_gains: Decimal      # Total realized gains
    total_losses: Decimal     # Total realized losses
    net_gains: Decimal        # Net gains (gains - losses)
    exemption_applied: Decimal # €1,270 exemption applied
    taxable_gains: Decimal    # Gains subject to tax
    tax_due: Decimal          # Tax amount (33% of taxable gains)
    created_at: datetime      # Report generation timestamp
    transactions_count: int   # Number of transactions included
    exchanges: List[str]      # Exchanges included in report
```

**Validation Rules**:
- `tax_year` must be valid Irish tax year (2010-2030)
- `total_gains` and `total_losses` must be non-negative
- `exemption_applied` must be €1,270 or less
- `tax_due` must be 33% of taxable gains

### Exchange
**Purpose**: Exchange configuration and connection details
**Schema**:
```python
class Exchange:
    name: str                 # Exchange name (binance, revolut, etc.)
    type: str                 # api, csv, manual
    api_key: str              # API key (encrypted)
    api_secret: str           # API secret (encrypted)
    base_url: str             # API base URL
    rate_limit: int           # Requests per minute
    is_active: bool           # Whether exchange is enabled
    last_sync: datetime       # Last successful sync
    created_at: datetime      # Configuration creation timestamp
```

**Validation Rules**:
- `name` must be unique
- `type` must be one of: api, csv, manual
- `api_key` and `api_secret` must be encrypted if present
- `rate_limit` must be positive

### Portfolio Snapshot
**Purpose**: Point-in-time portfolio valuation
**Schema**:
```python
class PortfolioSnapshot:
    id: str                   # Snapshot identifier
    date: datetime            # Snapshot timestamp
    total_value_eur: Decimal  # Total portfolio value in EUR
    holdings: Dict[str, Decimal] # Asset -> quantity
    asset_values: Dict[str, Decimal] # Asset -> EUR value
    realized_gains: Decimal   # Total realized gains
    unrealized_gains: Decimal # Total unrealized gains
    created_at: datetime      # Snapshot creation timestamp
```

**Validation Rules**:
- `total_value_eur` must be non-negative
- `holdings` and `asset_values` must have matching keys
- `date` must be within reasonable range

### Tax Year Summary
**Purpose**: Aggregated CGT data for tax year
**Schema**:
```python
class TaxYearSummary:
    tax_year: int             # Irish tax year
    total_gains: Decimal      # Total gains from all sources
    total_losses: Decimal     # Total losses from all sources
    net_position: Decimal     # Net gains/losses
    exemption_available: Decimal # Remaining exemption
    tax_due: Decimal          # Tax amount due
    transactions_count: int   # Number of transactions
    exchanges: List[str]      # Exchanges included
    last_updated: datetime    # Last calculation timestamp
```

**Validation Rules**:
- `tax_year` must be valid Irish tax year
- `exemption_available` must be €1,270 or less
- `tax_due` must be 33% of taxable gains

## Relationships

### Transaction Relationships
- `Transaction.exchange` → `Exchange.name` (many-to-one)
- `Transaction.asset` → `Asset.symbol` (many-to-one)
- `Transaction` → `CGTReport` (many-to-one, via tax_year)

### Portfolio Relationships
- `PortfolioSnapshot.holdings` → `Asset.symbol` (many-to-many)
- `PortfolioSnapshot` → `Transaction` (one-to-many, via date range)

### Report Relationships
- `CGTReport` → `Transaction` (one-to-many, via tax_year)
- `CGTReport` → `TaxYearSummary` (one-to-one, via tax_year)

## Data Validation Rules

### Transaction Validation
1. **Amount Validation**: Buy transactions must have positive amounts, sell transactions must have negative amounts
2. **Price Validation**: All prices must be positive and in EUR
3. **Date Validation**: Transaction dates must be within reasonable range and properly timezone-adjusted
4. **Fee Validation**: Fees must be non-negative and properly allocated
5. **Taxable Event Validation**: Only buy/sell/swap transactions are taxable

### CGT Calculation Validation
1. **FIFO Validation**: Cost basis must be calculated using FIFO method
2. **Tax Year Validation**: Transactions must be assigned to correct Irish tax year
3. **Exemption Validation**: €1,270 exemption must be applied correctly
4. **Rate Validation**: 33% tax rate must be applied to taxable gains
5. **Loss Carryover Validation**: Losses must be carried forward to future years

### Data Integrity Validation
1. **Source Attribution**: Every transaction must have clear source attribution
2. **Audit Trail**: All data changes must be logged with timestamps
3. **Reconciliation**: API and CSV data must be reconciled and discrepancies flagged
4. **Version Control**: Data snapshots must be immutable and versioned

## Database Schema

### Tables
- `transactions` - Main transaction records
- `assets` - Cryptocurrency metadata
- `cgt_reports` - Generated tax reports
- `exchanges` - Exchange configurations
- `portfolio_snapshots` - Portfolio valuations
- `tax_year_summaries` - Annual CGT summaries
- `data_snapshots` - Immutable API data snapshots
- `audit_logs` - Data change audit trail

### Indexes
- `transactions_date_idx` - Date-based queries
- `transactions_exchange_idx` - Exchange-based queries
- `transactions_asset_idx` - Asset-based queries
- `transactions_tax_year_idx` - Tax year queries
- `cgt_reports_tax_year_idx` - Report lookups

### Constraints
- Foreign key constraints between related tables
- Check constraints for data validation
- Unique constraints for business keys
- Not null constraints for required fields
