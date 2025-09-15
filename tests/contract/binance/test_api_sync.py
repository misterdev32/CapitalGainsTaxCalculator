"""
Contract tests for Binance API sync functionality.

These tests define the expected behavior and interface for the Binance API sync service
before implementation. Following TDD principles, these tests will fail initially and
guide the implementation.

Test Categories:
- API Authentication and Rate Limiting
- Data Fetching and Pagination
- Data Normalization and Validation
- Error Handling and Retry Logic
- Data Storage and Audit Trail
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from crypto_tax_calculator.services.binance_service import BinanceService
from crypto_tax_calculator.models.transaction import Transaction
from crypto_tax_calculator.models.asset import Asset


class TestBinanceAPISync:
    """Contract tests for Binance API sync service."""
    
    @pytest.fixture
    def binance_service(self):
        """Create a Binance service instance for testing."""
        return BinanceService(
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://api.binance.com"
        )
    
    @pytest.fixture
    def sample_binance_trade(self):
        """Sample Binance trade data as returned by API."""
        return {
            "symbol": "BTCUSDT",
            "id": 12345,
            "orderId": 67890,
            "orderListId": -1,
            "price": "50000.00000000",
            "qty": "0.00100000",
            "quoteQty": "50.00000000",
            "commission": "0.00000100",
            "commissionAsset": "BTC",
            "time": 1640995200000,  # 2022-01-01 00:00:00 UTC
            "isBuyer": True,
            "isMaker": False,
            "isBestMatch": True
        }
    
    @pytest.fixture
    def sample_binance_deposit(self):
        """Sample Binance deposit data as returned by API."""
        return {
            "amount": "0.1",
            "coin": "BTC",
            "network": "BTC",
            "status": 1,
            "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "addressTag": "",
            "txId": "tx123456789",
            "insertTime": 1640995200000,
            "transferType": 0,
            "confirmTimes": "12/12"
        }
    
    @pytest.fixture
    def sample_binance_withdrawal(self):
        """Sample Binance withdrawal data as returned by API."""
        return {
            "id": "987654321",
            "amount": "0.05",
            "transactionFee": "0.0005",
            "coin": "BTC",
            "status": 6,
            "address": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
            "addressTag": "",
            "txId": "tx987654321",
            "applyTime": "2022-01-01 12:00:00",
            "network": "BTC",
            "transferType": 1
        }

    def test_binance_service_initialization(self, binance_service):
        """Test that Binance service initializes correctly."""
        assert binance_service.api_key == "test_key"
        assert binance_service.api_secret == "test_secret"
        assert binance_service.base_url == "https://api.binance.com"
        assert binance_service.rate_limiter is not None
        assert binance_service.session is not None

    def test_authenticate_api_credentials(self, binance_service):
        """Test API authentication with valid credentials."""
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = {"serverTime": 1640995200000}
            
            result = binance_service.authenticate()
            
            assert result is True
            mock_request.assert_called_once_with("GET", "/api/v3/time")

    def test_authenticate_invalid_credentials(self, binance_service):
        """Test API authentication with invalid credentials."""
        binance_service.api_key = "invalid_key"
        binance_service.api_secret = "invalid_secret"
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.side_effect = Exception("Invalid API credentials")
            
            result = binance_service.authenticate()
            
            assert result is False

    def test_fetch_account_info(self, binance_service):
        """Test fetching account information."""
        mock_response = {
            "makerCommission": 15,
            "takerCommission": 15,
            "buyerCommission": 0,
            "sellerCommission": 0,
            "canTrade": True,
            "canWithdraw": True,
            "canDeposit": True,
            "updateTime": 1640995200000,
            "accountType": "SPOT",
            "balances": [
                {"asset": "BTC", "free": "0.1", "locked": "0.0"},
                {"asset": "ETH", "free": "1.0", "locked": "0.0"}
            ]
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            result = binance_service.get_account_info()
            
            assert result == mock_response
            mock_request.assert_called_once_with("GET", "/api/v3/account")

    def test_fetch_trade_history_with_pagination(self, binance_service):
        """Test fetching trade history with pagination support."""
        # Mock first page response
        first_page = {
            "trades": [
                {
                    "symbol": "BTCUSDT",
                    "id": 1,
                    "price": "50000.00000000",
                    "qty": "0.00100000",
                    "time": 1640995200000,
                    "isBuyer": True
                }
            ],
            "hasMore": True
        }
        
        # Mock second page response
        second_page = {
            "trades": [
                {
                    "symbol": "BTCUSDT", 
                    "id": 2,
                    "price": "51000.00000000",
                    "qty": "0.00200000",
                    "time": 1640995260000,
                    "isBuyer": False
                }
            ],
            "hasMore": False
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.side_effect = [first_page, second_page]
            
            trades = binance_service.get_trade_history(
                symbol="BTCUSDT",
                start_time=datetime(2022, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2022, 1, 2, tzinfo=timezone.utc)
            )
            
            assert len(trades) == 2
            assert trades[0]["id"] == 1
            assert trades[1]["id"] == 2
            assert mock_request.call_count == 2

    def test_fetch_deposit_history(self, binance_service):
        """Test fetching deposit history."""
        mock_response = {
            "depositList": [
                {
                    "amount": "0.1",
                    "coin": "BTC",
                    "network": "BTC",
                    "status": 1,
                    "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                    "txId": "tx123456789",
                    "insertTime": 1640995200000
                }
            ],
            "success": True
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            deposits = binance_service.get_deposit_history(
                start_time=datetime(2022, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2022, 1, 2, tzinfo=timezone.utc)
            )
            
            assert deposits == mock_response["depositList"]
            mock_request.assert_called_once()

    def test_fetch_withdrawal_history(self, binance_service):
        """Test fetching withdrawal history."""
        mock_response = {
            "withdrawList": [
                {
                    "id": "987654321",
                    "amount": "0.05",
                    "transactionFee": "0.0005",
                    "coin": "BTC",
                    "status": 6,
                    "address": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
                    "txId": "tx987654321",
                    "applyTime": "2022-01-01 12:00:00"
                }
            ],
            "success": True
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            withdrawals = binance_service.get_withdrawal_history(
                start_time=datetime(2022, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2022, 1, 2, tzinfo=timezone.utc)
            )
            
            assert withdrawals == mock_response["withdrawList"]
            mock_request.assert_called_once()

    def test_normalize_trade_to_transaction(self, binance_service, sample_binance_trade):
        """Test converting Binance trade to normalized Transaction."""
        with patch.object(binance_service, '_get_eur_price') as mock_price:
            mock_price.return_value = Decimal("42000.00")
            
            transaction = binance_service._normalize_trade(sample_binance_trade)
            
            assert isinstance(transaction, Transaction)
            assert transaction.exchange == "binance"
            assert transaction.asset == "BTC"
            assert transaction.action == "buy"
            assert transaction.amount == Decimal("0.001")
            assert transaction.price_eur == Decimal("42000.00")
            assert transaction.fee == Decimal("0.000001")
            assert transaction.fee_asset == "BTC"
            assert transaction.tx_id == "12345"
            assert transaction.source == "api"
            assert transaction.is_taxable is True

    def test_normalize_deposit_to_transaction(self, binance_service, sample_binance_deposit):
        """Test converting Binance deposit to normalized Transaction."""
        with patch.object(binance_service, '_get_eur_price') as mock_price:
            mock_price.return_value = Decimal("42000.00")
            
            transaction = binance_service._normalize_deposit(sample_binance_deposit)
            
            assert isinstance(transaction, Transaction)
            assert transaction.exchange == "binance"
            assert transaction.asset == "BTC"
            assert transaction.action == "transfer"
            assert transaction.amount == Decimal("0.1")
            assert transaction.price_eur == Decimal("42000.00")
            assert transaction.fee == Decimal("0")
            assert transaction.tx_id == "tx123456789"
            assert transaction.source == "api"
            assert transaction.is_taxable is False  # Deposits are not taxable

    def test_normalize_withdrawal_to_transaction(self, binance_service, sample_binance_withdrawal):
        """Test converting Binance withdrawal to normalized Transaction."""
        with patch.object(binance_service, '_get_eur_price') as mock_price:
            mock_price.return_value = Decimal("42000.00")
            
            transaction = binance_service._normalize_withdrawal(sample_binance_withdrawal)
            
            assert isinstance(transaction, Transaction)
            assert transaction.exchange == "binance"
            assert transaction.asset == "BTC"
            assert transaction.action == "transfer"
            assert transaction.amount == Decimal("-0.05")  # Negative for withdrawal
            assert transaction.price_eur == Decimal("42000.00")
            assert transaction.fee == Decimal("0.0005")
            assert transaction.tx_id == "tx987654321"
            assert transaction.source == "api"
            assert transaction.is_taxable is False  # Withdrawals are not taxable

    def test_rate_limiting_behavior(self, binance_service):
        """Test that rate limiting is properly implemented."""
        with patch.object(binance_service.rate_limiter, 'acquire') as mock_acquire:
            mock_acquire.return_value = True
            
            binance_service._make_request("GET", "/api/v3/time")
            
            mock_acquire.assert_called_once()

    def test_retry_logic_on_failure(self, binance_service):
        """Test retry logic when API calls fail."""
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.side_effect = [
                Exception("Rate limit exceeded"),
                Exception("Rate limit exceeded"), 
                {"serverTime": 1640995200000}
            ]
            
            result = binance_service.authenticate()
            
            assert result is True
            assert mock_request.call_count == 3

    def test_sync_transactions_complete_workflow(self, binance_service):
        """Test complete sync workflow from API to database."""
        # Mock API responses
        mock_trades = [{"symbol": "BTCUSDT", "id": 1, "price": "50000", "qty": "0.001", "time": 1640995200000, "isBuyer": True}]
        mock_deposits = [{"amount": "0.1", "coin": "BTC", "txId": "tx123", "insertTime": 1640995200000}]
        mock_withdrawals = [{"amount": "0.05", "coin": "BTC", "txId": "tx456", "applyTime": "2022-01-01 12:00:00"}]
        
        with patch.object(binance_service, 'get_trade_history') as mock_trades_func, \
             patch.object(binance_service, 'get_deposit_history') as mock_deposits_func, \
             patch.object(binance_service, 'get_withdrawal_history') as mock_withdrawals_func, \
             patch.object(binance_service, '_normalize_trade') as mock_normalize_trade, \
             patch.object(binance_service, '_normalize_deposit') as mock_normalize_deposit, \
             patch.object(binance_service, '_normalize_withdrawal') as mock_normalize_withdrawal, \
             patch.object(binance_service, '_save_transactions') as mock_save:
            
            mock_trades_func.return_value = mock_trades
            mock_deposits_func.return_value = mock_deposits
            mock_withdrawals_func.return_value = mock_withdrawals
            
            # Mock normalized transactions
            trade_tx = Transaction(id="1", exchange="binance", asset="BTC", action="buy", amount=Decimal("0.001"))
            deposit_tx = Transaction(id="2", exchange="binance", asset="BTC", action="transfer", amount=Decimal("0.1"))
            withdrawal_tx = Transaction(id="3", exchange="binance", asset="BTC", action="transfer", amount=Decimal("-0.05"))
            
            mock_normalize_trade.return_value = trade_tx
            mock_normalize_deposit.return_value = deposit_tx
            mock_normalize_withdrawal.return_value = withdrawal_tx
            
            # Execute sync
            result = binance_service.sync_transactions(
                start_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2022, 1, 2, tzinfo=timezone.utc)
            )
            
            # Verify all methods were called
            mock_trades_func.assert_called_once()
            mock_deposits_func.assert_called_once()
            mock_withdrawals_func.assert_called_once()
            mock_save.assert_called_once()
            
            # Verify result
            assert result["trades_synced"] == 1
            assert result["deposits_synced"] == 1
            assert result["withdrawals_synced"] == 1
            assert result["total_transactions"] == 3

    def test_error_handling_invalid_symbol(self, binance_service):
        """Test error handling for invalid symbol."""
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.side_effect = Exception("Invalid symbol")
            
            with pytest.raises(Exception, match="Invalid symbol"):
                binance_service.get_trade_history(symbol="INVALID")

    def test_error_handling_network_timeout(self, binance_service):
        """Test error handling for network timeout."""
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.side_effect = Exception("Network timeout")
            
            with pytest.raises(Exception, match="Network timeout"):
                binance_service.authenticate()

    def test_data_validation_transaction_fields(self, binance_service):
        """Test that normalized transactions have all required fields."""
        sample_trade = {
            "symbol": "BTCUSDT",
            "id": 12345,
            "price": "50000.00000000",
            "qty": "0.00100000",
            "time": 1640995200000,
            "isBuyer": True
        }
        
        with patch.object(binance_service, '_get_eur_price') as mock_price:
            mock_price.return_value = Decimal("42000.00")
            
            transaction = binance_service._normalize_trade(sample_trade)
            
            # Verify all required fields are present
            assert hasattr(transaction, 'id')
            assert hasattr(transaction, 'date')
            assert hasattr(transaction, 'exchange')
            assert hasattr(transaction, 'asset')
            assert hasattr(transaction, 'action')
            assert hasattr(transaction, 'amount')
            assert hasattr(transaction, 'price_eur')
            assert hasattr(transaction, 'fee')
            assert hasattr(transaction, 'fee_asset')
            assert hasattr(transaction, 'tx_id')
            assert hasattr(transaction, 'source')
            assert hasattr(transaction, 'is_taxable')
            assert hasattr(transaction, 'tax_year')

    def test_audit_trail_creation(self, binance_service):
        """Test that audit trail is created for sync operations."""
        with patch.object(binance_service, '_create_audit_record') as mock_audit:
            binance_service.sync_transactions(
                start_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2022, 1, 2, tzinfo=timezone.utc)
            )
            
            mock_audit.assert_called_once()
            audit_data = mock_audit.call_args[0][0]
            assert audit_data["operation"] == "binance_sync"
            assert "start_date" in audit_data
            assert "end_date" in audit_data
            assert "timestamp" in audit_data
