# Implementation Plan: Crypto Capital Gains Tax Calculator

**Branch**: `001-a-personalized-version` | **Date**: 2025-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-a-personalized-version/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build a crypto capital gains tax calculator that aggregates transactions from Binance (API), Revolut (CSV), and other exchanges, calculates Irish CGT obligations using FIFO method, and provides audit-proof reporting with data visualizations. The system uses a hybrid approach with API-first data collection, immutable snapshots for audit compliance, and comprehensive data reconciliation.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: pandas, requests, sqlite3, streamlit, plotly, python-binance, openpyxl  
**Storage**: SQLite (development) → PostgreSQL (production)  
**Testing**: pytest, pytest-asyncio, requests-mock  
**Target Platform**: Cross-platform (Windows/macOS/Linux)  
**Project Type**: single (CLI + web dashboard)  
**Performance Goals**: Handle 100k+ transactions, <5s report generation, <30s data sync  
**Constraints**: <2GB memory usage, offline-capable CSV processing, audit-compliant data retention  
**Scale/Scope**: Personal use (single user), 5+ exchanges, 3+ years of transaction history  

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: [2] (crypto-tax-calculator, crypto-tax-web)
- Using framework directly? (yes - pandas, streamlit, python-binance)
- Single data model? (yes - unified transaction schema)
- Avoiding patterns? (yes - direct database access, no Repository pattern)

**Architecture**:
- EVERY feature as library? (yes - core library + web interface)
- Libraries listed: [crypto-tax-calculator (core logic), crypto-tax-web (dashboard)]
- CLI per library: [crypto-tax-calculator --help/--version/--format, crypto-tax-web --help/--version]
- Library docs: llms.txt format planned? (yes)

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? (yes - tests written first)
- Git commits show tests before implementation? (yes)
- Order: Contract→Integration→E2E→Unit strictly followed? (yes)
- Real dependencies used? (yes - real SQLite, real API calls in integration tests)
- Integration tests for: new libraries, contract changes, shared schemas? (yes)
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? (yes - JSON logging with context)
- Frontend logs → backend? (unified logging stream)
- Error context sufficient? (yes - full transaction context in errors)

**Versioning**:
- Version number assigned? (yes - 1.0.0)
- BUILD increments on every change? (yes)
- Breaking changes handled? (yes - parallel tests, migration plan)

## Project Structure

### Documentation (this feature)
```
specs/001-a-personalized-version/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Single project with two main components
src/
├── crypto_tax_calculator/     # Core library
│   ├── __init__.py
│   ├── models/
│   │   ├── transaction.py
│   │   ├── asset.py
│   │   └── cgt_report.py
│   ├── services/
│   │   ├── binance_api.py
│   │   ├── csv_importer.py
│   │   ├── cgt_calculator.py
│   │   └── data_reconciler.py
│   ├── cli/
│   │   └── main.py
│   └── utils/
│       ├── rate_limiter.py
│       └── data_validator.py
├── crypto_tax_web/           # Web dashboard
│   ├── __init__.py
│   ├── dashboard.py
│   ├── components/
│   │   ├── charts.py
│   │   └── reports.py
│   └── cli/
│       └── main.py
└── shared/
    ├── database.py
    └── config.py

tests/
├── contract/
│   ├── test_binance_api.py
│   └── test_csv_importer.py
├── integration/
│   ├── test_data_pipeline.py
│   └── test_cgt_calculations.py
└── unit/
    ├── test_models.py
    └── test_services.py

data/
├── snapshots/           # Immutable API data snapshots
├── csv_exports/         # CSV files from exchanges
└── reports/            # Generated CGT reports
```

**Structure Decision**: Single project with two main libraries (core + web) for simplicity

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Binance API rate limiting and pagination strategies
   - Irish CGT calculation edge cases and exemptions
   - Data reconciliation patterns for API vs CSV sources
   - Streamlit dashboard architecture for financial data
   - SQLite to PostgreSQL migration strategy

2. **Generate and dispatch research agents**:
   ```
   Task: "Research Binance API rate limiting and pagination best practices for crypto tax applications"
   Task: "Research Irish CGT calculation requirements and edge cases for cryptocurrency"
   Task: "Research data reconciliation patterns for financial data from multiple sources"
   Task: "Research Streamlit dashboard patterns for financial data visualization"
   Task: "Research SQLite to PostgreSQL migration strategies for financial applications"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all technical decisions resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Transaction, Asset, CGT Report, Exchange, Portfolio Snapshot, Tax Year Summary
   - Validation rules from requirements
   - State transitions for data processing pipeline

2. **Generate API contracts** from functional requirements:
   - Binance API integration endpoints
   - CSV import/export endpoints
   - CGT calculation endpoints
   - Report generation endpoints
   - Output OpenAPI schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally**:
   - Run `/scripts/bash/update-agent-context.sh cursor` for Cursor
   - Add crypto tax calculation context
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 2 projects instead of 1 | Core library needs to be reusable independently of web interface | Single project would couple web dependencies with core logic |
| Separate database layer | Financial data requires ACID compliance and audit trails | Direct file access insufficient for transaction integrity |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*