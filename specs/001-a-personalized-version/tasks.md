# Tasks: Crypto Capital Gains Tax Calculator

**Input**: Design documents from `/specs/001-a-personalized-version/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 3.1: Setup
- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with dependencies (pandas, streamlit, python-binance, sqlalchemy, pytest)
- [ ] T003 [P] Configure linting and formatting tools (black, flake8, mypy)
- [ ] T004 [P] Set up database configuration (SQLite for dev, PostgreSQL for prod)
- [ ] T005 [P] Create environment configuration and secrets management
- [ ] T006 [P] Set up logging configuration with structured JSON logging

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [ ] T007 [P] Contract test Binance API sync in tests/contract/test_binance_api_sync.py
- [ ] T008 [P] Contract test Binance API status in tests/contract/test_binance_api_status.py
- [ ] T009 [P] Contract test Binance API transactions in tests/contract/test_binance_api_transactions.py
- [ ] T010 [P] Contract test CSV import in tests/contract/test_csv_import.py
- [ ] T011 [P] Contract test CSV validation in tests/contract/test_csv_validation.py
- [ ] T012 [P] Contract test CSV templates in tests/contract/test_csv_templates.py
- [ ] T013 [P] Contract test CGT calculation in tests/contract/test_cgt_calculation.py
- [ ] T014 [P] Contract test CGT reports in tests/contract/test_cgt_reports.py
- [ ] T015 [P] Contract test CGT export in tests/contract/test_cgt_export.py
- [ ] T016 [P] Contract test tax year transactions in tests/contract/test_tax_year_transactions.py

### Integration Tests
- [ ] T017 [P] Integration test complete data pipeline in tests/integration/test_data_pipeline.py
- [ ] T018 [P] Integration test CGT calculations in tests/integration/test_cgt_calculations.py
- [ ] T019 [P] Integration test data reconciliation in tests/integration/test_data_reconciliation.py
- [ ] T020 [P] Integration test rate limiting in tests/integration/test_rate_limiting.py
- [ ] T021 [P] Integration test audit trail in tests/integration/test_audit_trail.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [ ] T022 [P] Transaction model in src/crypto_tax_calculator/models/transaction.py
- [ ] T023 [P] Asset model in src/crypto_tax_calculator/models/asset.py
- [ ] T024 [P] CGT Report model in src/crypto_tax_calculator/models/cgt_report.py
- [ ] T025 [P] Exchange model in src/crypto_tax_calculator/models/exchange.py
- [ ] T026 [P] Portfolio Snapshot model in src/crypto_tax_calculator/models/portfolio_snapshot.py
- [ ] T027 [P] Tax Year Summary model in src/crypto_tax_calculator/models/tax_year_summary.py

### Core Services
- [ ] T028 [P] Binance API service in src/crypto_tax_calculator/services/binance_api.py
- [ ] T029 [P] CSV importer service in src/crypto_tax_calculator/services/csv_importer.py
- [ ] T030 [P] CGT calculator service in src/crypto_tax_calculator/services/cgt_calculator.py
- [ ] T031 [P] Data reconciler service in src/crypto_tax_calculator/services/data_reconciler.py
- [ ] T032 [P] Rate limiter utility in src/crypto_tax_calculator/utils/rate_limiter.py
- [ ] T033 [P] Data validator utility in src/crypto_tax_calculator/utils/data_validator.py

### Database Layer
- [ ] T034 [P] Database configuration in src/shared/database.py
- [ ] T035 [P] Database models and migrations in src/shared/models.py
- [ ] T036 [P] Database connection manager in src/shared/connection_manager.py

### CLI Commands
- [ ] T037 [P] Main CLI entry point in src/crypto_tax_calculator/cli/main.py
- [ ] T038 [P] Binance sync command in src/crypto_tax_calculator/cli/binance_commands.py
- [ ] T039 [P] CSV import command in src/crypto_tax_calculator/cli/csv_commands.py
- [ ] T040 [P] CGT calculation command in src/crypto_tax_calculator/cli/cgt_commands.py
- [ ] T041 [P] Report export command in src/crypto_tax_calculator/cli/export_commands.py

## Phase 3.4: Integration

### API Endpoints
- [ ] T042 [P] Binance API endpoints in src/crypto_tax_calculator/api/binance_endpoints.py
- [ ] T043 [P] CSV importer endpoints in src/crypto_tax_calculator/api/csv_endpoints.py
- [ ] T044 [P] CGT calculator endpoints in src/crypto_tax_calculator/api/cgt_endpoints.py
- [ ] T045 [P] API router configuration in src/crypto_tax_calculator/api/router.py

### Web Dashboard
- [ ] T046 [P] Streamlit dashboard main in src/crypto_tax_web/dashboard.py
- [ ] T047 [P] Portfolio charts component in src/crypto_tax_web/components/charts.py
- [ ] T048 [P] Reports component in src/crypto_tax_web/components/reports.py
- [ ] T049 [P] Web CLI entry point in src/crypto_tax_web/cli/main.py

### Data Processing Pipeline
- [ ] T050 [P] Data normalization pipeline in src/crypto_tax_calculator/pipelines/normalization.py
- [ ] T051 [P] FIFO calculation pipeline in src/crypto_tax_calculator/pipelines/fifo_calculator.py
- [ ] T052 [P] Tax year assignment pipeline in src/crypto_tax_calculator/pipelines/tax_year_assigner.py
- [ ] T053 [P] Data snapshot pipeline in src/crypto_tax_calculator/pipelines/snapshot_manager.py

## Phase 3.5: Polish

### Unit Tests
- [ ] T054 [P] Unit tests for models in tests/unit/test_models.py
- [ ] T055 [P] Unit tests for services in tests/unit/test_services.py
- [ ] T056 [P] Unit tests for utilities in tests/unit/test_utils.py
- [ ] T057 [P] Unit tests for pipelines in tests/unit/test_pipelines.py

### Performance and Optimization
- [ ] T058 [P] Performance tests for large datasets in tests/performance/test_large_datasets.py
- [ ] T059 [P] Database optimization and indexing in src/shared/optimization.py
- [ ] T060 [P] Caching implementation in src/crypto_tax_calculator/utils/cache.py

### Documentation and Final Polish
- [ ] T061 [P] API documentation in docs/api.md
- [ ] T062 [P] User guide in docs/user_guide.md
- [ ] T063 [P] Developer documentation in docs/developer_guide.md
- [ ] T064 [P] Configuration examples in docs/configuration.md
- [ ] T065 [P] Troubleshooting guide in docs/troubleshooting.md

## Dependencies
- Tests (T007-T021) before implementation (T022-T065)
- T022-T027 (models) block T028-T033 (services)
- T028-T033 (services) block T034-T036 (database)
- T034-T036 (database) block T042-T045 (API endpoints)
- T042-T045 (API endpoints) block T046-T049 (web dashboard)
- T050-T053 (pipelines) depend on T022-T027 (models)
- Implementation before polish (T054-T065)

## Parallel Execution Examples

### Phase 3.2: Contract Tests (T007-T016)
```
# Launch all contract tests together:
Task: "Contract test Binance API sync in tests/contract/test_binance_api_sync.py"
Task: "Contract test Binance API status in tests/contract/test_binance_api_status.py"
Task: "Contract test Binance API transactions in tests/contract/test_binance_api_transactions.py"
Task: "Contract test CSV import in tests/contract/test_csv_import.py"
Task: "Contract test CSV validation in tests/contract/test_csv_validation.py"
Task: "Contract test CSV templates in tests/contract/test_csv_templates.py"
Task: "Contract test CGT calculation in tests/contract/test_cgt_calculation.py"
Task: "Contract test CGT reports in tests/contract/test_cgt_reports.py"
Task: "Contract test CGT export in tests/contract/test_cgt_export.py"
Task: "Contract test tax year transactions in tests/contract/test_tax_year_transactions.py"
```

### Phase 3.2: Integration Tests (T017-T021)
```
# Launch all integration tests together:
Task: "Integration test complete data pipeline in tests/integration/test_data_pipeline.py"
Task: "Integration test CGT calculations in tests/integration/test_cgt_calculations.py"
Task: "Integration test data reconciliation in tests/integration/test_data_reconciliation.py"
Task: "Integration test rate limiting in tests/integration/test_rate_limiting.py"
Task: "Integration test audit trail in tests/integration/test_audit_trail.py"
```

### Phase 3.3: Data Models (T022-T027)
```
# Launch all model creation together:
Task: "Transaction model in src/crypto_tax_calculator/models/transaction.py"
Task: "Asset model in src/crypto_tax_calculator/models/asset.py"
Task: "CGT Report model in src/crypto_tax_calculator/models/cgt_report.py"
Task: "Exchange model in src/crypto_tax_calculator/models/exchange.py"
Task: "Portfolio Snapshot model in src/crypto_tax_calculator/models/portfolio_snapshot.py"
Task: "Tax Year Summary model in src/crypto_tax_calculator/models/tax_year_summary.py"
```

### Phase 3.3: Core Services (T028-T033)
```
# Launch all service creation together:
Task: "Binance API service in src/crypto_tax_calculator/services/binance_api.py"
Task: "CSV importer service in src/crypto_tax_calculator/services/csv_importer.py"
Task: "CGT calculator service in src/crypto_tax_calculator/services/cgt_calculator.py"
Task: "Data reconciler service in src/crypto_tax_calculator/services/data_reconciler.py"
Task: "Rate limiter utility in src/crypto_tax_calculator/utils/rate_limiter.py"
Task: "Data validator utility in src/crypto_tax_calculator/utils/data_validator.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
- Follow TDD: Red → Green → Refactor cycle
- All financial calculations must be precise (use Decimal type)
- All API calls must include proper error handling and retry logic
- All data changes must be logged for audit compliance

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
