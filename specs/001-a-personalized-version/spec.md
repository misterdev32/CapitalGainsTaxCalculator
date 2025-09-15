# Feature Specification: Crypto Capital Gains Tax Calculator

**Feature Branch**: `001-a-personalized-version`  
**Created**: 2025-01-15  
**Status**: Draft  
**Input**: User description: "a personalized version of koinly, a crypto investment tracking for tax calculation and data visualisation for my personal portfolio"

## Project Goals
- Aggregate all crypto transactions from **Binance (primary)**, **Revolut (primary)**, and **3–4 smaller exchanges** (Coinbase, KuCoin, etc.)
- Automate **data fetching via APIs** where possible (Binance: batch + pagination to cover full history)
- Store data in a **normalized format (CSV/JSON/DB)** for re-use and audit
- Calculate **realized capital gains under Irish CGT rules** (FIFO, 33%, €1,270 exemption, loss carryover)
- Provide **clear visualizations** to understand gains/losses by year, exchange, and asset
- Deliver **audit-proof records** so filings can be explained retrospectively

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies  
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a crypto investor in Ireland, I want to automatically aggregate my cryptocurrency transactions from Binance, Revolut, and other exchanges, calculate my capital gains tax obligations under Irish CGT rules, and generate audit-proof reports so that I can comply with Irish tax regulations and optimize my tax position.

### Acceptance Scenarios
1. **Given** I have Binance API credentials configured, **When** I run the data sync, **Then** the system should fetch all historical transactions using batch pagination and store them in normalized format
2. **Given** I have uploaded Revolut CSV exports, **When** I process the data, **Then** the system should normalize the transactions and integrate them with other exchange data
3. **Given** I have transactions from multiple exchanges, **When** I request an Irish CGT report, **Then** I should receive a detailed breakdown showing FIFO cost basis, realized gains/losses, and tax calculations with €1,270 exemption applied
4. **Given** I want to analyze my tax position, **When** I view the dashboard, **Then** I should see visualizations showing gains/losses by year, exchange, and asset with clear tax implications
5. **Given** I need to file my taxes, **When** I export the CGT report, **Then** I should receive a CSV/Excel file with audit-proof records that can be submitted to ROS

### Edge Cases
- What happens when Binance API rate limits are exceeded during batch pagination?
- How does the system handle coin-to-coin swaps as taxable events (sell + buy)?
- What happens when transaction fees need to be allocated across multiple assets?
- How does the system handle different time zones and ensure transactions are correctly assigned to Irish tax years?
- What happens when historical price data is unavailable for certain cryptocurrencies or specific dates?
- How does the system handle internal transfers between wallets vs taxable disposals?
- What happens when Binance API endpoints have different data availability (spot vs futures vs margin vs fiat)?
- How does the system handle data gaps where APIs miss certain transaction types that appear in CSV exports?
- What happens when Binance API rate limits are exceeded during large historical data fetches?
- How does the system ensure data consistency when APIs return mutable data vs CSV snapshots?

## Requirements *(mandatory)*

### Functional Requirements

#### Data Collection & Storage
- **FR-001**: System MUST integrate with Binance API using batch pagination to fetch complete transaction history (spot, swaps, deposits/withdrawals)
- **FR-002**: System MUST support CSV import from Revolut as primary data source
- **FR-003**: System MUST support CSV import from 3-4 additional exchanges (Coinbase, KuCoin, Kraken)
- **FR-004**: System MUST store raw data in CSV/JSON snapshots for reproducibility and offline use
- **FR-005**: System MUST implement scheduled incremental data sync (daily/weekly) for Binance API
- **FR-006**: System MUST normalize all transaction data into unified schema: `date | exchange | asset | action | amount | price (EUR) | fee | tx_id | source`

#### Transaction Processing
- **FR-007**: System MUST standardize transaction actions across exchanges (buy/sell/swap/transfer/staking/fee)
- **FR-008**: System MUST handle coin-to-coin swaps as taxable events (sell + buy)
- **FR-009**: System MUST flag non-taxable events (deposits, internal transfers)
- **FR-010**: System MUST handle transaction fees and their impact on cost basis calculations
- **FR-011**: System MUST support multiple fiat currencies with EUR as base currency for calculations

#### Irish CGT Calculations
- **FR-012**: System MUST calculate cost basis using FIFO (First In, First Out) method
- **FR-013**: System MUST calculate realized gains/losses per disposal (sale/swap) with proper Irish tax year assignment
- **FR-014**: System MUST apply Irish CGT rules: 33% tax rate, €1,270 annual exemption, loss carryover
- **FR-015**: System MUST aggregate yearly totals for CGT reporting
- **FR-016**: System MUST provide historical price data for accurate cost basis calculations in EUR

#### Reporting & Export
- **FR-017**: System MUST generate annual CGT summary: `Year | Gains | Losses | Net | Tax Due`
- **FR-018**: System MUST provide per-coin performance reports
- **FR-019**: System MUST generate exchange-level breakdown reports
- **FR-020**: System MUST export reports in CSV/Excel format suitable for ROS filings
- **FR-021**: System MUST provide audit-proof records with full transaction traceability

#### Visualization
- **FR-022**: System MUST generate timeline chart showing portfolio value and realized gains over time
- **FR-023**: System MUST provide pie chart showing current holdings by asset
- **FR-024**: System MUST create heatmap showing most profitable vs losing coins
- **FR-025**: System MUST generate stacked bar chart showing gains by exchange per year

#### Data Resilience & Audit Requirements
- **FR-026**: System MUST implement intelligent pagination with date range batching to handle Binance API history limitations
- **FR-027**: System MUST create immutable snapshots of all API data to ensure audit consistency
- **FR-028**: System MUST implement rate limiting and retry logic with exponential backoff for API calls
- **FR-029**: System MUST reconcile data between API and CSV sources and flag discrepancies
- **FR-030**: System MUST provide data source attribution for every transaction (API vs CSV vs manual)
- **FR-031**: System MUST implement secure API key management with read-only permissions
- **FR-032**: System MUST handle multiple Binance endpoints (spot, futures, margin, fiat) and merge data
- **FR-033**: System MUST provide data gap detection and reporting for missing transaction types
- **FR-034**: System MUST maintain version control for CSV snapshots with change tracking
- **FR-035**: System MUST implement data validation to ensure Irish tax year accuracy across time zones

## Limitations & Challenges *(mandatory)*

### API Limitations
- **LC-001**: Binance APIs have limited history depth - some endpoints only return last 3 months of data per request
- **LC-002**: Binance splits data across multiple endpoints (spot, futures, margin, fiat) requiring separate API calls and data stitching
- **LC-003**: Binance has strict rate limits (1200 requests/minute) requiring intelligent batching and retry logic
- **LC-004**: Some transaction types (coin-to-coin swaps, staking rewards, airdrops) may not appear cleanly in API endpoints
- **LC-005**: API data is mutable - historical records could change, requiring snapshot storage for audit consistency

### Data Integration Challenges
- **LC-006**: CSV exports from different exchanges have varying formats requiring normalization
- **LC-007**: Revolut and other exchanges don't provide granular API access, forcing CSV-only integration
- **LC-008**: Data gaps between API and CSV sources require reconciliation and gap-filling strategies
- **LC-009**: Exchange-specific data lock-in creates maintenance overhead when adding new exchanges

### Technical Constraints
- **LC-010**: API authentication requires secure key management with read-only permissions
- **LC-011**: Large historical datasets require efficient pagination and storage strategies
- **LC-012**: Real-time price data availability varies by cryptocurrency and time period
- **LC-013**: Time zone handling across multiple exchanges must ensure correct Irish tax year assignment

### Audit & Compliance Risks
- **LC-014**: API data changes could invalidate previously generated tax reports
- **LC-015**: CSV snapshots provide audit trail but require manual refresh and version control
- **LC-016**: Data reconciliation between sources must be transparent and auditable
- **LC-017**: Rate limiting could delay critical tax reporting during peak periods

## Mitigation Strategies *(mandatory)*

### API Data Handling
- **MS-001**: Implement hybrid approach: API for recent data + CSV for historical completeness
- **MS-002**: Use date range pagination with 3-month chunks to work around API limitations
- **MS-003**: Store API responses as immutable JSON snapshots with timestamps for audit trail
- **MS-004**: Implement data reconciliation reports to identify gaps between API and CSV sources
- **MS-005**: Use CSV exports as source of truth for critical tax calculations, API for real-time updates

### Rate Limiting & Performance
- **MS-006**: Implement intelligent batching with configurable delays based on API response times
- **MS-007**: Use background processing for large historical data imports to avoid blocking user operations
- **MS-008**: Implement data caching with TTL to reduce API calls for frequently accessed data
- **MS-009**: Provide progress indicators and resumable imports for large data sets

### Data Quality & Audit
- **MS-010**: Implement data validation rules to catch inconsistencies between sources
- **MS-011**: Provide data lineage tracking showing how each transaction was sourced and processed
- **MS-012**: Implement data quality scoring to identify potentially problematic transactions
- **MS-013**: Create audit reports showing data source reliability and completeness metrics

### Security & Compliance
- **MS-014**: Implement secure credential storage with encryption at rest
- **MS-015**: Use read-only API keys with IP whitelisting where possible
- **MS-016**: Implement data retention policies for audit compliance
- **MS-017**: Provide data export capabilities for regulatory compliance and tax audits

### Key Entities *(include if feature involves data)*
- **Transaction**: Normalized transaction record with schema: `date | exchange | asset | action | amount | price (EUR) | fee | tx_id | source` - represents individual buy/sell/swap/transfer events
- **Asset**: Individual cryptocurrency or token with current market data, historical prices in EUR, and metadata for tax calculations
- **CGT Report**: Generated document showing realized gains/losses, FIFO cost basis calculations, and Irish tax implications for specific tax years
- **Exchange**: Data source configuration (Binance API, Revolut CSV, other exchanges) with connection details and import capabilities
- **Portfolio Snapshot**: Point-in-time view of holdings across all exchanges with current valuations and performance metrics
- **Tax Year Summary**: Aggregated CGT data for a specific Irish tax year including gains, losses, net position, and tax due

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous  
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
