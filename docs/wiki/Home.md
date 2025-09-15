# Crypto Capital Gains Tax Calculator

Welcome to the Crypto Capital Gains Tax Calculator project! This tool helps Irish crypto investors calculate their Capital Gains Tax obligations with automated data collection, FIFO calculations, and audit-proof reporting.

## 🎯 Project Overview

This project provides a comprehensive solution for crypto tax compliance in Ireland, featuring:

- **Automated Data Collection**: Binance API integration with batch pagination
- **Multi-Exchange Support**: CSV import from Revolut, Coinbase, KuCoin, and others
- **Irish CGT Compliance**: FIFO calculations with €1,270 exemption and 33% tax rate
- **Audit-Proof Reporting**: Immutable data snapshots and comprehensive audit trails
- **Data Visualization**: Interactive dashboards for portfolio analysis

## 📚 Documentation

### Getting Started
- [Installation Guide](Installation-Guide)
- [Quick Start Tutorial](Quick-Start-Tutorial)
- [Configuration](Configuration)

### Development
- [Development Setup](Development-Setup)
- [Architecture Overview](Architecture-Overview)
- [API Documentation](API-Documentation)
- [Testing Guide](Testing-Guide)

### User Guides
- [User Manual](User-Manual)
- [Troubleshooting](Troubleshooting)
- [FAQ](FAQ)

### Project Management
- [Task Progress](Task-Progress)
- [Release Notes](Release-Notes)
- [Contributing](Contributing)

## 🚀 Quick Links

- [GitHub Repository](https://github.com/misterdev32/CapitalGainsTaxCalculator)
- [Issues](https://github.com/misterdev32/CapitalGainsTaxCalculator/issues)
- [Project Board](https://github.com/users/misterdev32/projects/1)
- [Wiki Home](https://github.com/misterdev32/CapitalGainsTaxCalculator/wiki)

## 📊 Project Status

- **Phase**: MVP Complete ✅
- **Total Tasks**: 65
- **Completed**: 18 (MVP + Setup + Tests)
- **In Progress**: 0
- **Remaining**: 47

## 🏗️ Architecture

The project follows a modular architecture with two main components:

1. **Core Library** (`crypto_tax_calculator`): Data processing, CGT calculations, API integrations
2. **Web Dashboard** (`crypto_tax_web`): Streamlit-based user interface

## 🎉 MVP Features

### ✅ Core Functionality
- **Multi-Exchange Support**: Binance API, Revolut, Coinbase, KuCoin, Kraken CSV
- **Irish CGT Calculation**: FIFO method, 33% tax rate, €1,270 exemption
- **Data Import**: CSV upload and API sync with auto-detection
- **Portfolio Analysis**: Asset allocation, transaction summaries
- **Tax Reports**: Detailed CGT calculations with audit trail

### ✅ User Interfaces
- **CLI Interface**: Full command-line functionality
- **Web Dashboard**: Streamlit-based web interface
- **Data Visualization**: Charts and tables for portfolio analysis

### ✅ Data Management
- **SQLite Database**: Local data storage with SQLAlchemy ORM
- **Data Validation**: Input validation and error handling
- **Audit Trail**: Complete transaction history and calculations

## 🔧 Tech Stack

- **Language**: Python 3.11+
- **Data Processing**: pandas, SQLAlchemy
- **Web Interface**: Streamlit, Plotly
- **APIs**: python-binance, requests
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Testing**: pytest, coverage
- **CI/CD**: GitHub Actions

## 📈 Development Phases

1. **Phase 3.1**: Setup and Configuration
2. **Phase 3.2**: Test-Driven Development
3. **Phase 3.3**: Core Implementation
4. **Phase 3.4**: Integration
5. **Phase 3.5**: Polish and Optimization

---

*Last updated: 2025-09-15*
