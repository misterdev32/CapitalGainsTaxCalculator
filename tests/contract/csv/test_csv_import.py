"""
Contract tests for CSV import functionality.

These tests define the expected behavior for importing transaction data
from various exchanges via CSV files before implementation.
"""

import pytest
import pandas as pd
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

from crypto_tax_calculator.services.csv_importer import CSVImporter
from crypto_tax_calculator.models.transaction import Transaction


class TestCSVImport:
    """Contract tests for CSV import functionality."""
    
    @pytest.fixture
    def csv_importer(self):
        """Create a CSV importer instance for testing."""
        return CSVImporter()
    
    @pytest.fixture
    def sample_revolut_csv_data(self):
        """Sample Revolut CSV data."""
        return pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",
                "Completed Date": "2022-01-01 12:00:00",
                "Description": "Bought 0.001 BTC for 50.00 EUR",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            },
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-02 12:00:00",
                "Completed Date": "2022-01-02 12:00:00",
                "Description": "Sold 0.001 BTC for 52.00 EUR",
                "Amount": "-0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "52.00",
                "Fiat amount (ex. fees)": "51.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
        ])
    
    @pytest.fixture
    def sample_coinbase_csv_data(self):
        """Sample Coinbase CSV data."""
        return pd.DataFrame([
            {
                "Timestamp": "2022-01-01T12:00:00Z",
                "Transaction Type": "Buy",
                "Asset": "BTC",
                "Quantity Transacted": "0.001",
                "EUR Spot Price at Transaction": "50000.00",
                "EUR Sub Total": "50.00",
                "EUR Total (inclusive of fees)": "50.50",
                "EUR Fees": "0.50",
                "Notes": "Bought 0.001 BTC"
            },
            {
                "Timestamp": "2022-01-02T12:00:00Z",
                "Transaction Type": "Sell",
                "Asset": "BTC",
                "Quantity Transacted": "0.001",
                "EUR Spot Price at Transaction": "52000.00",
                "EUR Sub Total": "52.00",
                "EUR Total (inclusive of fees)": "51.50",
                "EUR Fees": "0.50",
                "Notes": "Sold 0.001 BTC"
            }
        ])
    
    @pytest.fixture
    def sample_kucoin_csv_data(self):
        """Sample KuCoin CSV data."""
        return pd.DataFrame([
            {
                "UID": "123456789",
                "Account Type": "Main Account",
                "Order ID": "67890",
                "Order Type": "Buy",
                "Side": "Buy",
                "Symbol": "BTC-USDT",
                "Amount": "0.001",
                "Order Price": "50000.00",
                "Order Value": "50.00",
                "Fee": "0.05",
                "Fee Currency": "USDT",
                "Created Time": "2022-01-01 12:00:00",
                "Updated Time": "2022-01-01 12:00:00",
                "Status": "Filled"
            }
        ])
    
    @pytest.fixture
    def sample_kraken_csv_data(self):
        """Sample Kraken CSV data."""
        return pd.DataFrame([
            {
                "txid": "tx123456789",
                "ordertxid": "ord67890",
                "pair": "XXBTZEUR",
                "time": "1640995200.0000",
                "type": "buy",
                "ordertype": "market",
                "price": "50000.00",
                "cost": "50.00",
                "fee": "0.25",
                "vol": "0.001",
                "margin": "0.00000000",
                "misc": "",
                "ledgers": "L123456789"
            }
        ])

    def test_csv_importer_initialization(self, csv_importer):
        """Test CSV importer initialization."""
        assert csv_importer.supported_exchanges == ["revolut", "coinbase", "kucoin", "kraken"]
        assert csv_importer.validators is not None
        assert csv_importer.normalizers is not None

    def test_detect_exchange_from_csv_revolut(self, csv_importer, sample_revolut_csv_data):
        """Test detecting Revolut exchange from CSV structure."""
        exchange = csv_importer.detect_exchange(sample_revolut_csv_data)
        assert exchange == "revolut"

    def test_detect_exchange_from_csv_coinbase(self, csv_importer, sample_coinbase_csv_data):
        """Test detecting Coinbase exchange from CSV structure."""
        exchange = csv_importer.detect_exchange(sample_coinbase_csv_data)
        assert exchange == "coinbase"

    def test_detect_exchange_from_csv_kucoin(self, csv_importer, sample_kucoin_csv_data):
        """Test detecting KuCoin exchange from CSV structure."""
        exchange = csv_importer.detect_exchange(sample_kucoin_csv_data)
        assert exchange == "kucoin"

    def test_detect_exchange_from_csv_kraken(self, csv_importer, sample_kraken_csv_data):
        """Test detecting Kraken exchange from CSV structure."""
        exchange = csv_importer.detect_exchange(sample_kraken_csv_data)
        assert exchange == "kraken"

    def test_detect_exchange_unknown(self, csv_importer):
        """Test detecting unknown exchange from CSV structure."""
        unknown_data = pd.DataFrame([{"unknown_column": "value"}])
        
        with pytest.raises(ValueError, match="Unsupported exchange format"):
            csv_importer.detect_exchange(unknown_data)

    def test_validate_csv_structure_revolut(self, csv_importer, sample_revolut_csv_data):
        """Test validating Revolut CSV structure."""
        is_valid, errors = csv_importer.validate_csv_structure(sample_revolut_csv_data, "revolut")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_csv_structure_coinbase(self, csv_importer, sample_coinbase_csv_data):
        """Test validating Coinbase CSV structure."""
        is_valid, errors = csv_importer.validate_csv_structure(sample_coinbase_csv_data, "coinbase")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_csv_structure_missing_columns(self, csv_importer):
        """Test validating CSV with missing required columns."""
        incomplete_data = pd.DataFrame([{"Type": "EXCHANGE"}])  # Missing required columns
        
        is_valid, errors = csv_importer.validate_csv_structure(incomplete_data, "revolut")
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("missing required column" in error.lower() for error in errors)

    def test_validate_csv_data_types_revolut(self, csv_importer, sample_revolut_csv_data):
        """Test validating Revolut CSV data types."""
        is_valid, errors = csv_importer.validate_csv_data_types(sample_revolut_csv_data, "revolut")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_csv_data_types_invalid(self, csv_importer):
        """Test validating CSV with invalid data types."""
        invalid_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "invalid_date",
                "Amount": "not_a_number",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "invalid_amount"
            }
        ])
        
        is_valid, errors = csv_importer.validate_csv_data_types(invalid_data, "revolut")
        
        assert is_valid is False
        assert len(errors) > 0

    def test_normalize_revolut_transactions(self, csv_importer, sample_revolut_csv_data):
        """Test normalizing Revolut transactions to standard format."""
        transactions = csv_importer.normalize_transactions(sample_revolut_csv_data, "revolut")
        
        assert len(transactions) == 2
        assert all(isinstance(tx, Transaction) for tx in transactions)
        
        # Check first transaction (buy)
        buy_tx = transactions[0]
        assert buy_tx.exchange == "revolut"
        assert buy_tx.asset == "BTC"
        assert buy_tx.action == "buy"
        assert buy_tx.amount == Decimal("0.001")
        assert buy_tx.price_eur == Decimal("49500.00")  # Excluding fees
        assert buy_tx.fee == Decimal("0.50")
        assert buy_tx.fee_asset == "EUR"
        assert buy_tx.source == "csv"
        assert buy_tx.is_taxable is True
        
        # Check second transaction (sell)
        sell_tx = transactions[1]
        assert sell_tx.exchange == "revolut"
        assert sell_tx.asset == "BTC"
        assert sell_tx.action == "sell"
        assert sell_tx.amount == Decimal("-0.001")  # Negative for sell
        assert sell_tx.price_eur == Decimal("51500.00")  # Excluding fees
        assert sell_tx.fee == Decimal("0.50")
        assert sell_tx.fee_asset == "EUR"
        assert sell_tx.source == "csv"
        assert sell_tx.is_taxable is True

    def test_normalize_coinbase_transactions(self, csv_importer, sample_coinbase_csv_data):
        """Test normalizing Coinbase transactions to standard format."""
        transactions = csv_importer.normalize_transactions(sample_coinbase_csv_data, "coinbase")
        
        assert len(transactions) == 2
        assert all(isinstance(tx, Transaction) for tx in transactions)
        
        # Check first transaction (buy)
        buy_tx = transactions[0]
        assert buy_tx.exchange == "coinbase"
        assert buy_tx.asset == "BTC"
        assert buy_tx.action == "buy"
        assert buy_tx.amount == Decimal("0.001")
        assert buy_tx.price_eur == Decimal("50000.00")
        assert buy_tx.fee == Decimal("0.50")
        assert buy_tx.fee_asset == "EUR"
        assert buy_tx.source == "csv"
        assert buy_tx.is_taxable is True

    def test_normalize_kucoin_transactions(self, csv_importer, sample_kucoin_csv_data):
        """Test normalizing KuCoin transactions to standard format."""
        with patch.object(csv_importer, '_convert_usdt_to_eur') as mock_convert:
            mock_convert.return_value = Decimal("42000.00")  # USDT to EUR conversion
            
            transactions = csv_importer.normalize_transactions(sample_kucoin_csv_data, "kucoin")
            
            assert len(transactions) == 1
            assert all(isinstance(tx, Transaction) for tx in transactions)
            
            tx = transactions[0]
            assert tx.exchange == "kucoin"
            assert tx.asset == "BTC"
            assert tx.action == "buy"
            assert tx.amount == Decimal("0.001")
            assert tx.price_eur == Decimal("42000.00")  # Converted from USDT
            assert tx.fee == Decimal("0.05")
            assert tx.fee_asset == "USDT"
            assert tx.source == "csv"
            assert tx.is_taxable is True

    def test_normalize_kraken_transactions(self, csv_importer, sample_kraken_csv_data):
        """Test normalizing Kraken transactions to standard format."""
        transactions = csv_importer.normalize_transactions(sample_kraken_csv_data, "kraken")
        
        assert len(transactions) == 1
        assert all(isinstance(tx, Transaction) for tx in transactions)
        
        tx = transactions[0]
        assert tx.exchange == "kraken"
        assert tx.asset == "BTC"
        assert tx.action == "buy"
        assert tx.amount == Decimal("0.001")
        assert tx.price_eur == Decimal("50000.00")
        assert tx.fee == Decimal("0.25")
        assert tx.fee_asset == "EUR"
        assert tx.source == "csv"
        assert tx.is_taxable is True

    def test_import_csv_file_success(self, csv_importer, tmp_path):
        """Test successful CSV file import."""
        # Create a temporary CSV file
        csv_file = tmp_path / "revolut_transactions.csv"
        sample_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
        ])
        sample_data.to_csv(csv_file, index=False)
        
        with patch.object(csv_importer, 'normalize_transactions') as mock_normalize:
            mock_normalize.return_value = [Transaction(id="1", exchange="revolut", asset="BTC")]
            
            result = csv_importer.import_csv_file(csv_file)
            
            assert result["success"] is True
            assert result["exchange"] == "revolut"
            assert result["transaction_count"] == 1
            assert "transactions" in result

    def test_import_csv_file_invalid_format(self, csv_importer, tmp_path):
        """Test importing CSV file with invalid format."""
        csv_file = tmp_path / "invalid.csv"
        invalid_data = pd.DataFrame([{"invalid_column": "value"}])
        invalid_data.to_csv(csv_file, index=False)
        
        result = csv_importer.import_csv_file(csv_file)
        
        assert result["success"] is False
        assert "error" in result
        assert "Unsupported exchange format" in result["error"]

    def test_import_csv_file_validation_errors(self, csv_importer, tmp_path):
        """Test importing CSV file with validation errors."""
        csv_file = tmp_path / "invalid_revolut.csv"
        invalid_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Amount": "not_a_number",  # Invalid data type
                "Currency": "BTC"
            }
        ])
        invalid_data.to_csv(csv_file, index=False)
        
        result = csv_importer.import_csv_file(csv_file)
        
        assert result["success"] is False
        assert "validation errors" in result["error"]

    def test_handle_duplicate_transactions(self, csv_importer):
        """Test handling duplicate transactions in CSV."""
        duplicate_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            },
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",  # Same timestamp
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
        ])
        
        with patch.object(csv_importer, '_detect_duplicates') as mock_detect:
            mock_detect.return_value = [1]  # Second row is duplicate
            
            transactions = csv_importer.normalize_transactions(duplicate_data, "revolut")
            
            assert len(transactions) == 1  # Only one transaction after deduplication

    def test_handle_missing_optional_fields(self, csv_importer):
        """Test handling missing optional fields in CSV."""
        incomplete_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "",  # Missing fee
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
        ])
        
        transactions = csv_importer.normalize_transactions(incomplete_data, "revolut")
        
        assert len(transactions) == 1
        assert transactions[0].fee == Decimal("0")  # Default to 0 for missing fee

    def test_convert_currency_to_eur(self, csv_importer):
        """Test currency conversion to EUR."""
        with patch.object(csv_importer, '_get_exchange_rate') as mock_rate:
            mock_rate.return_value = Decimal("0.85")  # USD to EUR rate
            
            eur_amount = csv_importer._convert_currency_to_eur(Decimal("100"), "USD")
            
            assert eur_amount == Decimal("85.00")
            mock_rate.assert_called_once_with("USD", "EUR")

    def test_parse_date_formats(self, csv_importer):
        """Test parsing various date formats."""
        # Test ISO format
        iso_date = csv_importer._parse_date("2022-01-01T12:00:00Z")
        assert iso_date.year == 2022
        assert iso_date.month == 1
        assert iso_date.day == 1
        assert iso_date.tzinfo == timezone.utc
        
        # Test custom format
        custom_date = csv_importer._parse_date("2022-01-01 12:00:00")
        assert custom_date.year == 2022
        assert custom_date.month == 1
        assert custom_date.day == 1
        
        # Test Unix timestamp
        unix_date = csv_importer._parse_date("1640995200")
        assert unix_date.year == 2022
        assert unix_date.month == 1
        assert unix_date.day == 1

    def test_validate_transaction_amounts(self, csv_importer):
        """Test validation of transaction amounts."""
        # Valid amounts
        assert csv_importer._validate_amount(Decimal("0.001")) is True
        assert csv_importer._validate_amount(Decimal("-0.001")) is True  # Negative for sells
        
        # Invalid amounts
        assert csv_importer._validate_amount(Decimal("0")) is False  # Zero amount
        assert csv_importer._validate_amount(Decimal("invalid")) is False  # Invalid decimal

    def test_generate_import_summary(self, csv_importer):
        """Test generating import summary."""
        transactions = [
            Transaction(id="1", exchange="revolut", asset="BTC", action="buy"),
            Transaction(id="2", exchange="revolut", asset="ETH", action="sell"),
            Transaction(id="3", exchange="coinbase", asset="BTC", action="buy")
        ]
        
        summary = csv_importer._generate_import_summary(transactions)
        
        assert summary["total_transactions"] == 3
        assert summary["exchanges"] == ["revolut", "coinbase"]
        assert summary["assets"] == ["BTC", "ETH"]
        assert summary["actions"] == ["buy", "sell"]
        assert "import_timestamp" in summary

    def test_handle_encoding_issues(self, csv_importer, tmp_path):
        """Test handling CSV files with different encodings."""
        # Create CSV with UTF-8 encoding
        csv_file = tmp_path / "utf8_transactions.csv"
        sample_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
        ])
        sample_data.to_csv(csv_file, index=False, encoding='utf-8')
        
        with patch.object(csv_importer, 'normalize_transactions') as mock_normalize:
            mock_normalize.return_value = [Transaction(id="1", exchange="revolut", asset="BTC")]
            
            result = csv_importer.import_csv_file(csv_file)
            
            assert result["success"] is True
            assert result["encoding"] == "utf-8"

    def test_handle_large_csv_files(self, csv_importer, tmp_path):
        """Test handling large CSV files with chunking."""
        # Create a large CSV file
        csv_file = tmp_path / "large_transactions.csv"
        large_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": f"2022-01-{i%30+1:02d} 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
            for i in range(1000)  # 1000 transactions
        ])
        large_data.to_csv(csv_file, index=False)
        
        with patch.object(csv_importer, 'normalize_transactions') as mock_normalize:
            mock_normalize.return_value = [Transaction(id=str(i), exchange="revolut", asset="BTC") for i in range(1000)]
            
            result = csv_importer.import_csv_file(csv_file, chunk_size=100)
            
            assert result["success"] is True
            assert result["transaction_count"] == 1000
            assert mock_normalize.call_count == 10  # 1000 / 100 = 10 chunks
