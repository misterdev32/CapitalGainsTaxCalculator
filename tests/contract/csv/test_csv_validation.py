"""
Contract tests for CSV validation functionality.

These tests define the expected behavior for validating CSV data
structure, content, and data types before implementation.
"""

import pytest
import pandas as pd
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

from crypto_tax_calculator.services.csv_validator import CSVValidator
from crypto_tax_calculator.models.transaction import Transaction


class TestCSVValidation:
    """Contract tests for CSV validation functionality."""
    
    @pytest.fixture
    def csv_validator(self):
        """Create a CSV validator instance for testing."""
        return CSVValidator()
    
    @pytest.fixture
    def valid_revolut_data(self):
        """Valid Revolut CSV data for testing."""
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
            }
        ])
    
    @pytest.fixture
    def invalid_revolut_data(self):
        """Invalid Revolut CSV data for testing."""
        return pd.DataFrame([
            {
                "Type": "INVALID_TYPE",  # Invalid transaction type
                "Product": "",  # Empty product
                "Started Date": "invalid_date",  # Invalid date format
                "Amount": "not_a_number",  # Invalid amount
                "Currency": "INVALID_CURRENCY",  # Invalid currency
                "Fiat amount (inc. fees)": "-50.00",  # Negative amount
                "Fee": "invalid_fee",  # Invalid fee
                "Base currency": "INVALID_BASE",  # Invalid base currency
                "State": "INVALID_STATE"  # Invalid state
            }
        ])

    def test_csv_validator_initialization(self, csv_validator):
        """Test CSV validator initialization."""
        assert csv_validator.supported_exchanges == ["revolut", "coinbase", "kucoin", "kraken"]
        assert csv_validator.validation_rules is not None
        assert csv_validator.data_type_validators is not None

    def test_validate_revolut_structure_valid(self, csv_validator, valid_revolut_data):
        """Test validating valid Revolut CSV structure."""
        is_valid, errors = csv_validator.validate_structure(valid_revolut_data, "revolut")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_revolut_structure_missing_columns(self, csv_validator):
        """Test validating Revolut CSV with missing required columns."""
        incomplete_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin"
                # Missing required columns
            }
        ])
        
        is_valid, errors = csv_validator.validate_structure(incomplete_data, "revolut")
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("missing required column" in error.lower() for error in errors)

    def test_validate_revolut_structure_extra_columns(self, csv_validator, valid_revolut_data):
        """Test validating Revolut CSV with extra columns."""
        # Add extra column
        valid_revolut_data["Extra Column"] = "extra_value"
        
        is_valid, errors = csv_validator.validate_structure(valid_revolut_data, "revolut")
        
        # Extra columns should not cause validation failure
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_coinbase_structure_valid(self, csv_validator):
        """Test validating valid Coinbase CSV structure."""
        valid_coinbase_data = pd.DataFrame([
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
            }
        ])
        
        is_valid, errors = csv_validator.validate_structure(valid_coinbase_data, "coinbase")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_kucoin_structure_valid(self, csv_validator):
        """Test validating valid KuCoin CSV structure."""
        valid_kucoin_data = pd.DataFrame([
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
        
        is_valid, errors = csv_validator.validate_structure(valid_kucoin_data, "kucoin")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_kraken_structure_valid(self, csv_validator):
        """Test validating valid Kraken CSV structure."""
        valid_kraken_data = pd.DataFrame([
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
        
        is_valid, errors = csv_validator.validate_structure(valid_kraken_data, "kraken")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_data_types_valid(self, csv_validator, valid_revolut_data):
        """Test validating valid data types."""
        is_valid, errors = csv_validator.validate_data_types(valid_revolut_data, "revolut")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_data_types_invalid(self, csv_validator, invalid_revolut_data):
        """Test validating invalid data types."""
        is_valid, errors = csv_validator.validate_data_types(invalid_revolut_data, "revolut")
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("invalid data type" in error.lower() for error in errors)

    def test_validate_transaction_type_revolut(self, csv_validator):
        """Test validating Revolut transaction types."""
        # Valid types
        assert csv_validator._validate_transaction_type("EXCHANGE", "revolut") is True
        assert csv_validator._validate_transaction_type("TRANSFER", "revolut") is True
        assert csv_validator._validate_transaction_type("CASHBACK", "revolut") is True
        
        # Invalid types
        assert csv_validator._validate_transaction_type("INVALID", "revolut") is False
        assert csv_validator._validate_transaction_type("", "revolut") is False

    def test_validate_transaction_type_coinbase(self, csv_validator):
        """Test validating Coinbase transaction types."""
        # Valid types
        assert csv_validator._validate_transaction_type("Buy", "coinbase") is True
        assert csv_validator._validate_transaction_type("Sell", "coinbase") is True
        assert csv_validator._validate_transaction_type("Send", "coinbase") is True
        assert csv_validator._validate_transaction_type("Receive", "coinbase") is True
        
        # Invalid types
        assert csv_validator._validate_transaction_type("INVALID", "coinbase") is False

    def test_validate_currency_codes(self, csv_validator):
        """Test validating currency codes."""
        # Valid currencies
        assert csv_validator._validate_currency("BTC") is True
        assert csv_validator._validate_currency("ETH") is True
        assert csv_validator._validate_currency("EUR") is True
        assert csv_validator._validate_currency("USD") is True
        assert csv_validator._validate_currency("USDT") is True
        
        # Invalid currencies
        assert csv_validator._validate_currency("INVALID") is False
        assert csv_validator._validate_currency("") is False
        assert csv_validator._validate_currency("123") is False

    def test_validate_amount_values(self, csv_validator):
        """Test validating amount values."""
        # Valid amounts
        assert csv_validator._validate_amount("0.001") is True
        assert csv_validator._validate_amount("1.0") is True
        assert csv_validator._validate_amount("100.50") is True
        assert csv_validator._validate_amount("-0.001") is True  # Negative for sells
        
        # Invalid amounts
        assert csv_validator._validate_amount("0") is False  # Zero amount
        assert csv_validator._validate_amount("not_a_number") is False
        assert csv_validator._validate_amount("") is False
        assert csv_validator._validate_amount("infinity") is False

    def test_validate_date_formats(self, csv_validator):
        """Test validating date formats."""
        # Valid dates
        assert csv_validator._validate_date("2022-01-01 12:00:00") is True
        assert csv_validator._validate_date("2022-01-01T12:00:00Z") is True
        assert csv_validator._validate_date("1640995200") is True  # Unix timestamp
        assert csv_validator._validate_date("2022-01-01") is True
        
        # Invalid dates
        assert csv_validator._validate_date("invalid_date") is False
        assert csv_validator._validate_date("") is False
        assert csv_validator._validate_date("32-01-2022") is False  # Invalid day
        assert csv_validator._validate_date("2022-13-01") is False  # Invalid month

    def test_validate_price_values(self, csv_validator):
        """Test validating price values."""
        # Valid prices
        assert csv_validator._validate_price("50000.00") is True
        assert csv_validator._validate_price("0.001") is True
        assert csv_validator._validate_price("1000000.50") is True
        
        # Invalid prices
        assert csv_validator._validate_price("0") is False  # Zero price
        assert csv_validator._validate_price("-100.00") is False  # Negative price
        assert csv_validator._validate_price("not_a_number") is False
        assert csv_validator._validate_price("") is False

    def test_validate_fee_values(self, csv_validator):
        """Test validating fee values."""
        # Valid fees
        assert csv_validator._validate_fee("0.50") is True
        assert csv_validator._validate_fee("0") is True  # Zero fee is valid
        assert csv_validator._validate_fee("100.00") is True
        
        # Invalid fees
        assert csv_validator._validate_fee("-0.50") is False  # Negative fee
        assert csv_validator._validate_fee("not_a_number") is False
        assert csv_validator._validate_fee("") is False

    def test_validate_state_values_revolut(self, csv_validator):
        """Test validating Revolut state values."""
        # Valid states
        assert csv_validator._validate_state("COMPLETED", "revolut") is True
        assert csv_validator._validate_state("PENDING", "revolut") is True
        assert csv_validator._validate_state("FAILED", "revolut") is True
        
        # Invalid states
        assert csv_validator._validate_state("INVALID", "revolut") is False
        assert csv_validator._validate_state("", "revolut") is False

    def test_validate_state_values_kucoin(self, csv_validator):
        """Test validating KuCoin state values."""
        # Valid states
        assert csv_validator._validate_state("Filled", "kucoin") is True
        assert csv_validator._validate_state("Cancelled", "kucoin") is True
        assert csv_validator._validate_state("Partial", "kucoin") is True
        
        # Invalid states
        assert csv_validator._validate_state("INVALID", "kucoin") is False

    def test_validate_symbol_format_kucoin(self, csv_validator):
        """Test validating KuCoin symbol format."""
        # Valid symbols
        assert csv_validator._validate_symbol("BTC-USDT", "kucoin") is True
        assert csv_validator._validate_symbol("ETH-USDT", "kucoin") is True
        assert csv_validator._validate_symbol("ADA-BTC", "kucoin") is True
        
        # Invalid symbols
        assert csv_validator._validate_symbol("BTCUSDT", "kucoin") is False  # Missing dash
        assert csv_validator._validate_symbol("BTC-", "kucoin") is False  # Incomplete
        assert csv_validator._validate_symbol("", "kucoin") is False

    def test_validate_pair_format_kraken(self, csv_validator):
        """Test validating Kraken pair format."""
        # Valid pairs
        assert csv_validator._validate_pair("XXBTZEUR", "kraken") is True
        assert csv_validator._validate_pair("XETHZEUR", "kraken") is True
        assert csv_validator._validate_pair("XXRPZEUR", "kraken") is True
        
        # Invalid pairs
        assert csv_validator._validate_pair("BTC-EUR", "kraken") is False  # Wrong format
        assert csv_validator._validate_pair("", "kraken") is False

    def test_validate_order_type_kraken(self, csv_validator):
        """Test validating Kraken order types."""
        # Valid order types
        assert csv_validator._validate_order_type("buy", "kraken") is True
        assert csv_validator._validate_order_type("sell", "kraken") is True
        
        # Invalid order types
        assert csv_validator._validate_order_type("INVALID", "kraken") is False
        assert csv_validator._validate_order_type("", "kraken") is False

    def test_validate_ordertype_kraken(self, csv_validator):
        """Test validating Kraken order types."""
        # Valid order types
        assert csv_validator._validate_ordertype("market", "kraken") is True
        assert csv_validator._validate_ordertype("limit", "kraken") is True
        assert csv_validator._validate_ordertype("stop-loss", "kraken") is True
        
        # Invalid order types
        assert csv_validator._validate_ordertype("INVALID", "kraken") is False

    def test_validate_required_fields_present(self, csv_validator, valid_revolut_data):
        """Test validating that all required fields are present."""
        is_valid, errors = csv_validator._validate_required_fields(valid_revolut_data, "revolut")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_required_fields_missing(self, csv_validator):
        """Test validating missing required fields."""
        incomplete_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin"
                # Missing required fields
            }
        ])
        
        is_valid, errors = csv_validator._validate_required_fields(incomplete_data, "revolut")
        
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_data_consistency(self, csv_validator):
        """Test validating data consistency across related fields."""
        # Consistent data
        consistent_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50"
            }
        ])
        
        is_valid, errors = csv_validator._validate_data_consistency(consistent_data, "revolut")
        assert is_valid is True
        assert len(errors) == 0
        
        # Inconsistent data (fee + ex. fees != inc. fees)
        inconsistent_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "1.00"  # Inconsistent: 49.50 + 1.00 != 50.00
            }
        ])
        
        is_valid, errors = csv_validator._validate_data_consistency(inconsistent_data, "revolut")
        assert is_valid is False
        assert len(errors) > 0
        assert any("inconsistent" in error.lower() for error in errors)

    def test_validate_date_range(self, csv_validator):
        """Test validating date ranges."""
        # Valid date range
        valid_data = pd.DataFrame([
            {
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC"
            }
        ])
        
        is_valid, errors = csv_validator._validate_date_range(valid_data, "revolut")
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid date range (future date)
        future_data = pd.DataFrame([
            {
                "Started Date": "2030-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC"
            }
        ])
        
        is_valid, errors = csv_validator._validate_date_range(future_data, "revolut")
        assert is_valid is False
        assert len(errors) > 0
        assert any("future date" in error.lower() for error in errors)

    def test_validate_duplicate_transactions(self, csv_validator):
        """Test validating duplicate transactions."""
        # No duplicates
        unique_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC"
            },
            {
                "Type": "EXCHANGE",
                "Started Date": "2022-01-02 12:00:00",
                "Amount": "0.002",
                "Currency": "BTC"
            }
        ])
        
        is_valid, errors = csv_validator._validate_duplicates(unique_data, "revolut")
        assert is_valid is True
        assert len(errors) == 0
        
        # With duplicates
        duplicate_data = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC"
            },
            {
                "Type": "EXCHANGE",
                "Started Date": "2022-01-01 12:00:00",  # Same timestamp
                "Amount": "0.001",  # Same amount
                "Currency": "BTC"  # Same currency
            }
        ])
        
        is_valid, errors = csv_validator._validate_duplicates(duplicate_data, "revolut")
        assert is_valid is False
        assert len(errors) > 0
        assert any("duplicate" in error.lower() for error in errors)

    def test_comprehensive_validation(self, csv_validator, valid_revolut_data):
        """Test comprehensive validation of all aspects."""
        is_valid, errors = csv_validator.validate_comprehensive(valid_revolut_data, "revolut")
        
        assert is_valid is True
        assert len(errors) == 0

    def test_comprehensive_validation_with_errors(self, csv_validator, invalid_revolut_data):
        """Test comprehensive validation with multiple errors."""
        is_valid, errors = csv_validator.validate_comprehensive(invalid_revolut_data, "revolut")
        
        assert is_valid is False
        assert len(errors) > 0
        # Should have multiple types of errors
        error_types = [error.split(":")[0] for error in errors]
        assert len(set(error_types)) > 1  # Multiple error types

    def test_validation_error_reporting(self, csv_validator, invalid_revolut_data):
        """Test detailed error reporting."""
        is_valid, errors = csv_validator.validate_comprehensive(invalid_revolut_data, "revolut")
        
        assert is_valid is False
        assert len(errors) > 0
        
        # Check error format
        for error in errors:
            assert ":" in error  # Should have format "Error Type: Description"
            assert len(error.split(":")) == 2  # Exactly one colon
        
        # Check error categories
        error_categories = [error.split(":")[0] for error in errors]
        expected_categories = ["Structure", "Data Type", "Value", "Consistency"]
        assert any(cat in error_categories for cat in expected_categories)

    def test_validation_performance(self, csv_validator):
        """Test validation performance with large datasets."""
        # Create large dataset
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
        
        import time
        start_time = time.time()
        is_valid, errors = csv_validator.validate_comprehensive(large_data, "revolut")
        end_time = time.time()
        
        assert is_valid is True
        assert len(errors) == 0
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
