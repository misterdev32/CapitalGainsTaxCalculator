# Crypto Capital Gains Tax Calculator

A comprehensive tool for Irish crypto investors to calculate Capital Gains Tax obligations with automated data collection, FIFO calculations, and audit-proof reporting.

## 🎯 Features

- **Automated Data Collection**: Binance API integration with batch pagination
- **Multi-Exchange Support**: CSV import from Revolut, Coinbase, KuCoin, and others
- **Irish CGT Compliance**: FIFO calculations with €1,270 exemption and 33% tax rate
- **Audit-Proof Reporting**: Immutable data snapshots and comprehensive audit trails
- **Data Visualization**: Interactive dashboards for portfolio analysis

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/misterdev32/CapitalGainsTaxCalculator.git
cd CapitalGainsTaxCalculator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -e .

# Initialize database
crypto-tax-calc init-db
```

### Basic Usage

```bash
# Configure Binance API
crypto-tax-calc configure-exchange --exchange binance --api-key YOUR_KEY --api-secret YOUR_SECRET

# Sync data from Binance
crypto-tax-calc sync-binance --start-date 2021-01-01 --end-date 2024-12-31

# Import CSV data
crypto-tax-calc import-csv --file revolut_transactions.csv --exchange revolut

# Calculate CGT for 2024
crypto-tax-calc calculate-cgt --tax-year 2024

# Launch web dashboard
crypto-tax-web start-dashboard
```

## 📚 Documentation

- [Installation Guide](docs/wiki/Installation-Guide.md)
- [Quick Start Tutorial](docs/wiki/Quick-Start-Tutorial.md)
- [User Manual](docs/wiki/User-Manual.md)
- [API Documentation](docs/wiki/API-Documentation.md)
- [Architecture Overview](docs/wiki/Architecture-Overview.md)

## 🏗️ Development

### Project Structure

```
src/
├── crypto_tax_calculator/     # Core library
│   ├── models/               # Data models
│   ├── services/             # Business logic
│   ├── cli/                  # Command-line interface
│   ├── api/                  # REST API endpoints
│   └── pipelines/            # Data processing pipelines
├── crypto_tax_web/           # Web dashboard
│   ├── components/           # UI components
│   └── cli/                  # Web CLI
└── shared/                   # Shared utilities
    └── database.py           # Database configuration
```

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src/ tests/
flake8 src/ tests/
mypy src/

# Run security checks
safety check
bandit -r src/
```

## 📊 Project Status

- **Phase**: Development (Phase 3.1: Setup)
- **Total Tasks**: 65
- **Completed**: 2
- **In Progress**: 0
- **Remaining**: 63

[View Task Progress](docs/wiki/Task-Progress.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

See [Contributing Guide](docs/wiki/Contributing.md) for detailed instructions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for informational purposes only and should not be considered as professional tax advice. Always consult with a qualified tax professional for your specific situation.

## 🔗 Links

- [GitHub Repository](https://github.com/misterdev32/CapitalGainsTaxCalculator)
- [Issues](https://github.com/misterdev32/CapitalGainsTaxCalculator/issues)
- [Project Board](https://github.com/users/misterdev32/projects/1)
- [Wiki](https://github.com/misterdev32/CapitalGainsTaxCalculator/wiki)

---

*Built with ❤️ for the Irish crypto community*
