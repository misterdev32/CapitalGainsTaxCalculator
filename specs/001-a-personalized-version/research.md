# Research: Crypto Capital Gains Tax Calculator

**Date**: 2025-01-15  
**Feature**: 001-a-personalized-version  
**Status**: Complete

## Research Areas

### 1. Binance API Rate Limiting and Pagination

**Decision**: Implement exponential backoff with 3-month date range pagination
- Use 3-month chunks for historical data fetching
- Implement exponential backoff starting at 1 second, max 60 seconds
- Use request queuing with priority for recent data

**Rationale**: 
- Binance rate limit is 1200 requests/minute (20 requests/second)
- Historical data requires pagination due to 3-month endpoint limitations
- Exponential backoff handles temporary rate limit violations gracefully

**Alternatives considered**:
- Fixed delay: Too slow for large datasets
- Linear backoff: Less efficient than exponential
- Single large requests: Not supported by Binance API

### 2. Irish CGT Calculation Requirements

**Decision**: Implement FIFO with Irish-specific rules
- 33% tax rate on realized gains
- €1,270 annual exemption per person
- Loss carryover to future years
- Tax year runs April 6 to April 5

**Rationale**:
- FIFO is the default method for Irish CGT
- Specific exemption amount and tax rate are legally required
- Tax year alignment is critical for compliance

**Alternatives considered**:
- LIFO: Not allowed for Irish CGT
- Specific identification: Too complex for automated system
- Average cost: Not recognized for Irish CGT

### 3. Data Reconciliation Patterns

**Decision**: Implement three-tier reconciliation approach
- Tier 1: API data as primary source for recent transactions
- Tier 2: CSV data as source of truth for historical completeness
- Tier 3: Manual reconciliation reports for discrepancies

**Rationale**:
- APIs provide real-time data but may have gaps
- CSV exports are complete but static
- Manual reconciliation ensures audit compliance

**Alternatives considered**:
- API-only: Risk of missing historical data
- CSV-only: No real-time updates
- Database-only: No audit trail of source data

### 4. Streamlit Dashboard Architecture

**Decision**: Use Streamlit with Plotly for financial visualizations
- Streamlit for rapid prototyping and deployment
- Plotly for interactive financial charts
- Session state for data persistence
- File upload for CSV imports

**Rationale**:
- Streamlit is ideal for data-heavy applications
- Plotly provides professional financial charting
- Session state handles large datasets efficiently
- File upload integrates well with CSV workflow

**Alternatives considered**:
- Flask + Chart.js: More complex setup
- Django + D3.js: Overkill for single-user application
- Jupyter notebooks: Not suitable for production

### 5. SQLite to PostgreSQL Migration

**Decision**: Use SQLAlchemy ORM with database abstraction
- SQLite for development and testing
- PostgreSQL for production
- Database-agnostic queries through SQLAlchemy
- Migration scripts for data transfer

**Rationale**:
- SQLite is perfect for development and testing
- PostgreSQL provides ACID compliance for financial data
- SQLAlchemy abstracts database differences
- Migration scripts ensure data integrity

**Alternatives considered**:
- Direct SQL: Database-specific code
- No migration: SQLite insufficient for production
- Database per environment: Complex deployment

## Technical Decisions Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| API Client | python-binance | Official library, handles rate limiting |
| Data Processing | pandas | Industry standard for financial data |
| Database ORM | SQLAlchemy | Database abstraction, migration support |
| Web Framework | Streamlit | Rapid development, data-focused |
| Visualization | Plotly | Professional financial charts |
| Testing | pytest | Python standard, async support |
| Rate Limiting | Custom exponential backoff | Handles Binance API constraints |

## Implementation Notes

- All API calls must include proper error handling and retry logic
- Data snapshots must be immutable with timestamps for audit trail
- CGT calculations must be validated against known test cases
- Dashboard must handle large datasets without performance issues
- Database migrations must be reversible and tested

## Risk Mitigation

- API rate limiting: Implement intelligent batching and caching
- Data accuracy: Use CSV exports as source of truth for critical calculations
- Performance: Implement data pagination and lazy loading
- Compliance: Maintain detailed audit logs and data lineage
- Security: Use read-only API keys and encrypt sensitive data
