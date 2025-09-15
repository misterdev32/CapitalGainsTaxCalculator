"""
Contract tests for Binance API transaction fetching and processing.

These tests define the expected behavior for fetching various types of transactions
from Binance API, including trades, deposits, withdrawals, and other transaction types.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from crypto_tax_calculator.services.binance_service import BinanceService
from crypto_tax_calculator.models.transaction import Transaction


class TestBinanceAPITransactions:
    """Contract tests for Binance API transaction operations."""
    
    @pytest.fixture
    def binance_service(self):
        """Create a Binance service instance for testing."""
        return BinanceService(
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://api.binance.com"
        )

    def test_fetch_all_trades(self, binance_service):
        """Test fetching all trades for a specific symbol."""
        mock_response = [
            {
                "symbol": "BTCUSDT",
                "id": 12345,
                "orderId": 67890,
                "price": "50000.00000000",
                "qty": "0.00100000",
                "quoteQty": "50.00000000",
                "commission": "0.00000100",
                "commissionAsset": "BTC",
                "time": 1640995200000,
                "isBuyer": True,
                "isMaker": False
            },
            {
                "symbol": "BTCUSDT",
                "id": 12346,
                "orderId": 67891,
                "price": "51000.00000000",
                "qty": "0.00200000",
                "quoteQty": "102.00000000",
                "commission": "0.00000200",
                "commissionAsset": "BTC",
                "time": 1640995260000,
                "isBuyer": False,
                "isMaker": True
            }
        ]
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            trades = binance_service.get_all_trades(symbol="BTCUSDT")
            
            assert len(trades) == 2
            assert trades[0]["id"] == 12345
            assert trades[1]["id"] == 12346
            mock_request.assert_called_once()

    def test_fetch_trades_with_date_range(self, binance_service):
        """Test fetching trades within a specific date range."""
        start_time = datetime(2022, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2022, 1, 2, tzinfo=timezone.utc)
        
        mock_response = [
            {
                "symbol": "BTCUSDT",
                "id": 12345,
                "price": "50000.00000000",
                "qty": "0.00100000",
                "time": 1640995200000,
                "isBuyer": True
            }
        ]
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            trades = binance_service.get_trades_by_date_range(
                symbol="BTCUSDT",
                start_time=start_time,
                end_time=end_time
            )
            
            assert len(trades) == 1
            mock_request.assert_called_once()

    def test_fetch_trades_with_pagination(self, binance_service):
        """Test fetching trades with pagination support."""
        # Mock first page
        first_page = {
            "trades": [
                {"symbol": "BTCUSDT", "id": 1, "price": "50000", "qty": "0.001", "time": 1640995200000, "isBuyer": True}
            ],
            "hasMore": True
        }
        
        # Mock second page
        second_page = {
            "trades": [
                {"symbol": "BTCUSDT", "id": 2, "price": "51000", "qty": "0.002", "time": 1640995260000, "isBuyer": False}
            ],
            "hasMore": False
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.side_effect = [first_page, second_page]
            
            trades = binance_service.get_trades_paginated(symbol="BTCUSDT", limit=1)
            
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
                    "addressTag": "",
                    "txId": "tx123456789",
                    "insertTime": 1640995200000,
                    "transferType": 0,
                    "confirmTimes": "12/12"
                },
                {
                    "amount": "1.0",
                    "coin": "ETH",
                    "network": "ETH",
                    "status": 1,
                    "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    "addressTag": "",
                    "txId": "tx987654321",
                    "insertTime": 1640995260000,
                    "transferType": 0,
                    "confirmTimes": "12/12"
                }
            ],
            "success": True
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            deposits = binance_service.get_deposit_history()
            
            assert len(deposits) == 2
            assert deposits[0]["coin"] == "BTC"
            assert deposits[1]["coin"] == "ETH"
            mock_request.assert_called_once()

    def test_fetch_deposit_history_with_coin_filter(self, binance_service):
        """Test fetching deposit history filtered by coin."""
        mock_response = {
            "depositList": [
                {
                    "amount": "0.1",
                    "coin": "BTC",
                    "network": "BTC",
                    "status": 1,
                    "txId": "tx123456789",
                    "insertTime": 1640995200000
                }
            ],
            "success": True
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            deposits = binance_service.get_deposit_history(coin="BTC")
            
            assert len(deposits) == 1
            assert deposits[0]["coin"] == "BTC"
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
                    "addressTag": "",
                    "txId": "tx987654321",
                    "applyTime": "2022-01-01 12:00:00",
                    "network": "BTC",
                    "transferType": 1
                }
            ],
            "success": True
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            withdrawals = binance_service.get_withdrawal_history()
            
            assert len(withdrawals) == 1
            assert withdrawals[0]["coin"] == "BTC"
            assert withdrawals[0]["amount"] == "0.05"
            mock_request.assert_called_once()

    def test_fetch_withdrawal_history_with_status_filter(self, binance_service):
        """Test fetching withdrawal history filtered by status."""
        mock_response = {
            "withdrawList": [
                {
                    "id": "987654321",
                    "amount": "0.05",
                    "coin": "BTC",
                    "status": 6,  # Completed
                    "txId": "tx987654321",
                    "applyTime": "2022-01-01 12:00:00"
                }
            ],
            "success": True
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            withdrawals = binance_service.get_withdrawal_history(status=6)
            
            assert len(withdrawals) == 1
            assert withdrawals[0]["status"] == 6
            mock_request.assert_called_once()

    def test_fetch_swap_history(self, binance_service):
        """Test fetching swap history."""
        mock_response = [
            {
                "swapId": 123456,
                "swapTime": 1640995200000,
                "status": 1,
                "quoteAsset": "USDT",
                "baseAsset": "BTC",
                "quoteQty": "1000.00000000",
                "baseQty": "0.02000000",
                "price": "50000.00000000",
                "fee": "0.10000000"
            }
        ]
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            swaps = binance_service.get_swap_history()
            
            assert len(swaps) == 1
            assert swaps[0]["swapId"] == 123456
            assert swaps[0]["baseAsset"] == "BTC"
            assert swaps[0]["quoteAsset"] == "USDT"
            mock_request.assert_called_once()

    def test_fetch_staking_rewards(self, binance_service):
        """Test fetching staking rewards."""
        mock_response = {
            "rows": [
                {
                    "asset": "ETH",
                    "amount": "0.01",
                    "time": 1640995200000,
                    "type": "STAKE_REWARDS",
                    "status": "SUCCESS"
                },
                {
                    "asset": "ADA",
                    "amount": "10.0",
                    "time": 1640995260000,
                    "type": "STAKE_REWARDS",
                    "status": "SUCCESS"
                }
            ],
            "total": 2
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            rewards = binance_service.get_staking_rewards()
            
            assert len(rewards) == 2
            assert rewards[0]["asset"] == "ETH"
            assert rewards[1]["asset"] == "ADA"
            mock_request.assert_called_once()

    def test_fetch_fee_history(self, binance_service):
        """Test fetching trading fee history."""
        mock_response = [
            {
                "symbol": "BTCUSDT",
                "makerCommission": "0.001",
                "takerCommission": "0.001",
                "time": 1640995200000
            }
        ]
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            fees = binance_service.get_fee_history()
            
            assert len(fees) == 1
            assert fees[0]["symbol"] == "BTCUSDT"
            assert fees[0]["makerCommission"] == "0.001"
            mock_request.assert_called_once()

    def test_fetch_dust_log(self, binance_service):
        """Test fetching dust conversion log."""
        mock_response = {
            "total": 1,
            "userAssetDribblets": [
                {
                    "operateTime": 1640995200000,
                    "totalTransferedAmount": "0.00100000",
                    "totalServiceChargeAmount": "0.00010000",
                    "transId": 123456789,
                    "userAssetDribbletDetails": [
                        {
                            "fromAsset": "BNB",
                            "amount": "0.00100000",
                            "toAsset": "USDT",
                            "transferedAmount": "0.00090000",
                            "serviceChargeAmount": "0.00010000"
                        }
                    ]
                }
            ]
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            dust_log = binance_service.get_dust_log()
            
            assert dust_log["total"] == 1
            assert len(dust_log["userAssetDribblets"]) == 1
            mock_request.assert_called_once()

    def test_fetch_convert_trade_history(self, binance_service):
        """Test fetching convert trade history."""
        mock_response = {
            "list": [
                {
                    "orderId": 123456789,
                    "orderStatus": "SUCCESS",
                    "fromAsset": "USDT",
                    "fromAmount": "100.00000000",
                    "toAsset": "BTC",
                    "toAmount": "0.00200000",
                    "ratio": "50000.00000000",
                    "inverseRatio": "0.00002000",
                    "createTime": 1640995200000,
                    "updateTime": 1640995200000
                }
            ],
            "startTime": 1640995200000,
            "endTime": 1640995260000,
            "limit": 100,
            "moreData": False
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            convert_trades = binance_service.get_convert_trade_history()
            
            assert len(convert_trades["list"]) == 1
            assert convert_trades["list"][0]["fromAsset"] == "USDT"
            assert convert_trades["list"][0]["toAsset"] == "BTC"
            mock_request.assert_called_once()

    def test_fetch_asset_dividend_history(self, binance_service):
        """Test fetching asset dividend history."""
        mock_response = {
            "rows": [
                {
                    "asset": "BNB",
                    "amount": "0.1",
                    "divTime": 1640995200000,
                    "enInfo": "BNB Vault Staking Rewards"
                }
            ],
            "total": 1
        }
        
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response
            
            dividends = binance_service.get_asset_dividend_history()
            
            assert len(dividends["rows"]) == 1
            assert dividends["rows"][0]["asset"] == "BNB"
            assert dividends["total"] == 1
            mock_request.assert_called_once()

    def test_fetch_all_transaction_types(self, binance_service):
        """Test fetching all transaction types in one call."""
        with patch.object(binance_service, 'get_all_trades') as mock_trades, \
             patch.object(binance_service, 'get_deposit_history') as mock_deposits, \
             patch.object(binance_service, 'get_withdrawal_history') as mock_withdrawals, \
             patch.object(binance_service, 'get_swap_history') as mock_swaps, \
             patch.object(binance_service, 'get_staking_rewards') as mock_staking:
            
            mock_trades.return_value = [{"id": 1, "symbol": "BTCUSDT"}]
            mock_deposits.return_value = [{"amount": "0.1", "coin": "BTC"}]
            mock_withdrawals.return_value = [{"amount": "0.05", "coin": "BTC"}]
            mock_swaps.return_value = [{"swapId": 123, "baseAsset": "BTC"}]
            mock_staking.return_value = [{"asset": "ETH", "amount": "0.01"}]
            
            all_transactions = binance_service.get_all_transactions()
            
            assert "trades" in all_transactions
            assert "deposits" in all_transactions
            assert "withdrawals" in all_transactions
            assert "swaps" in all_transactions
            assert "staking_rewards" in all_transactions
            assert len(all_transactions["trades"]) == 1
            assert len(all_transactions["deposits"]) == 1
            assert len(all_transactions["withdrawals"]) == 1
            assert len(all_transactions["swaps"]) == 1
            assert len(all_transactions["staking_rewards"]) == 1

    def test_fetch_transactions_with_date_range(self, binance_service):
        """Test fetching transactions within a specific date range."""
        start_time = datetime(2022, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2022, 1, 2, tzinfo=timezone.utc)
        
        with patch.object(binance_service, 'get_trades_by_date_range') as mock_trades, \
             patch.object(binance_service, 'get_deposit_history') as mock_deposits, \
             patch.object(binance_service, 'get_withdrawal_history') as mock_withdrawals:
            
            mock_trades.return_value = [{"id": 1, "time": 1640995200000}]
            mock_deposits.return_value = [{"amount": "0.1", "insertTime": 1640995200000}]
            mock_withdrawals.return_value = [{"amount": "0.05", "applyTime": "2022-01-01 12:00:00"}]
            
            transactions = binance_service.get_transactions_by_date_range(
                start_time=start_time,
                end_time=end_time
            )
            
            assert "trades" in transactions
            assert "deposits" in transactions
            assert "withdrawals" in transactions
            mock_trades.assert_called_once_with(
                symbol=None, start_time=start_time, end_time=end_time
            )

    def test_handle_api_errors_gracefully(self, binance_service):
        """Test handling API errors gracefully."""
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.side_effect = Exception("API rate limit exceeded")
            
            with pytest.raises(Exception, match="API rate limit exceeded"):
                binance_service.get_all_trades(symbol="BTCUSDT")

    def test_handle_empty_responses(self, binance_service):
        """Test handling empty API responses."""
        with patch.object(binance_service, '_make_request') as mock_request:
            mock_request.return_value = []
            
            trades = binance_service.get_all_trades(symbol="BTCUSDT")
            
            assert trades == []

    def test_handle_partial_failures(self, binance_service):
        """Test handling partial failures in transaction fetching."""
        with patch.object(binance_service, 'get_all_trades') as mock_trades, \
             patch.object(binance_service, 'get_deposit_history') as mock_deposits, \
             patch.object(binance_service, 'get_withdrawal_history') as mock_withdrawals:
            
            mock_trades.return_value = [{"id": 1, "symbol": "BTCUSDT"}]
            mock_deposits.side_effect = Exception("Deposit API error")
            mock_withdrawals.return_value = [{"amount": "0.05", "coin": "BTC"}]
            
            with pytest.raises(Exception, match="Deposit API error"):
                binance_service.get_all_transactions()

    def test_validate_transaction_data(self, binance_service):
        """Test validation of transaction data from API."""
        invalid_trade = {
            "symbol": "INVALID",  # Invalid symbol format
            "id": "not_a_number",  # Invalid ID
            "price": "-100.00",  # Negative price
            "qty": "0",  # Zero quantity
            "time": "invalid_time"  # Invalid timestamp
        }
        
        with pytest.raises(ValueError):
            binance_service._validate_trade_data(invalid_trade)

    def test_normalize_transaction_timestamps(self, binance_service):
        """Test normalization of transaction timestamps."""
        trade_with_timestamp = {
            "symbol": "BTCUSDT",
            "id": 12345,
            "price": "50000.00000000",
            "qty": "0.00100000",
            "time": 1640995200000,  # Unix timestamp in milliseconds
            "isBuyer": True
        }
        
        with patch.object(binance_service, '_get_eur_price') as mock_price:
            mock_price.return_value = Decimal("42000.00")
            
            transaction = binance_service._normalize_trade(trade_with_trade)
            
            assert isinstance(transaction.date, datetime)
            assert transaction.date.tzinfo == timezone.utc
            assert transaction.date.year == 2022
            assert transaction.date.month == 1
            assert transaction.date.day == 1

    def test_calculate_transaction_fees(self, binance_service):
        """Test calculation of transaction fees in EUR."""
        trade_with_fee = {
            "symbol": "BTCUSDT",
            "id": 12345,
            "price": "50000.00000000",
            "qty": "0.00100000",
            "commission": "0.00000100",
            "commissionAsset": "BTC",
            "time": 1640995200000,
            "isBuyer": True
        }
        
        with patch.object(binance_service, '_get_eur_price') as mock_price:
            mock_price.return_value = Decimal("42000.00")
            
            transaction = binance_service._normalize_trade(trade_with_fee)
            
            # Fee should be converted to EUR
            expected_fee_eur = Decimal("0.000001") * Decimal("42000.00")
            assert transaction.fee == expected_fee_eur
            assert transaction.fee_asset == "EUR"
