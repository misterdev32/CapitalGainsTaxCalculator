"""
Binance API service for fetching cryptocurrency transaction data.
"""

import time
import requests
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..models.transaction import Transaction
from ..models.asset import Asset
from shared.logging_config import get_logger

logger = get_logger(__name__)


class BinanceService:
    """Service for interacting with Binance API."""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.binance.com"):
        """Initialize Binance service."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        
        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
    
    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Binance API."""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
        
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key}
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            else:
                response = self.session.post(url, headers=headers, json=params, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Binance API request failed: {e}")
            raise Exception(f"Binance API request failed: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to Binance API."""
        try:
            response = self._make_request("GET", "/api/v3/time")
            return "serverTime" in response
        except Exception as e:
            logger.error(f"Binance connection test failed: {e}")
            return False
    
    def get_server_time(self) -> datetime:
        """Get server time from Binance."""
        response = self._make_request("GET", "/api/v3/time")
        server_time_ms = response["serverTime"]
        return datetime.fromtimestamp(server_time_ms / 1000, tz=timezone.utc)
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        params = {"timestamp": int(time.time() * 1000)}
        return self._make_request("GET", "/api/v3/account", params)
    
    def get_trade_history(self, symbol: str, start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get trade history for a symbol."""
        params = {"symbol": symbol}
        
        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)
        
        params["timestamp"] = int(time.time() * 1000)
        
        try:
            response = self._make_request("GET", "/api/v3/myTrades", params)
            return response
        except Exception as e:
            logger.error(f"Failed to get trade history for {symbol}: {e}")
            return []
    
    def get_deposit_history(self, start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get deposit history."""
        params = {"timestamp": int(time.time() * 1000)}
        
        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)
        
        try:
            response = self._make_request("GET", "/sapi/v1/capital/deposit/hisrec", params)
            return response.get("depositList", [])
        except Exception as e:
            logger.error(f"Failed to get deposit history: {e}")
            return []
    
    def get_withdrawal_history(self, start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get withdrawal history."""
        params = {"timestamp": int(time.time() * 1000)}
        
        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)
        
        try:
            response = self._make_request("GET", "/sapi/v1/capital/withdraw/history", params)
            return response.get("withdrawList", [])
        except Exception as e:
            logger.error(f"Failed to get withdrawal history: {e}")
            return []
    
    def _normalize_trade(self, trade: Dict[str, Any]) -> Transaction:
        """Normalize Binance trade to Transaction model."""
        # Extract basic information
        symbol = trade["symbol"]
        base_asset = symbol.replace("USDT", "").replace("BUSD", "").replace("EUR", "")
        
        # Determine action
        is_buyer = trade.get("isBuyer", False)
        action = "buy" if is_buyer else "sell"
        
        # Calculate amounts
        amount = Decimal(str(trade["qty"]))
        if not is_buyer:
            amount = -amount  # Negative for sells
        
        price_usdt = Decimal(str(trade["price"]))
        price_eur = self._convert_usdt_to_eur(price_usdt)
        
        # Calculate fees
        fee = Decimal(str(trade.get("commission", "0")))
        fee_asset = trade.get("commissionAsset", "USDT")
        if fee_asset == "USDT":
            fee_eur = self._convert_usdt_to_eur(fee)
        else:
            fee_eur = fee  # Assume already in EUR
        
        # Create transaction
        transaction = Transaction(
            id=f"binance_{trade['id']}",
            date=datetime.fromtimestamp(trade["time"] / 1000, tz=timezone.utc),
            exchange="binance",
            asset=base_asset,
            action=action,
            amount=amount,
            price_eur=price_eur,
            fee=fee_eur,
            fee_asset="EUR",
            tx_id=str(trade["id"]),
            source="api",
            is_taxable=True,
            tax_year=self._calculate_tax_year(datetime.fromtimestamp(trade["time"] / 1000, tz=timezone.utc)),
            description=f"Binance {action} {abs(amount)} {base_asset}"
        )
        
        return transaction
    
    def _normalize_deposit(self, deposit: Dict[str, Any]) -> Transaction:
        """Normalize Binance deposit to Transaction model."""
        # Extract information
        asset = deposit["coin"]
        amount = Decimal(str(deposit["amount"]))
        
        # Get EUR price
        price_eur = self._get_asset_price_eur(asset)
        
        # Create transaction
        transaction = Transaction(
            id=f"binance_deposit_{deposit['txId']}",
            date=datetime.fromtimestamp(deposit["insertTime"] / 1000, tz=timezone.utc),
            exchange="binance",
            asset=asset,
            action="transfer",
            amount=amount,
            price_eur=price_eur,
            fee=Decimal("0"),
            fee_asset="EUR",
            tx_id=deposit["txId"],
            source="api",
            is_taxable=False,  # Deposits are not taxable
            tax_year=self._calculate_tax_year(datetime.fromtimestamp(deposit["insertTime"] / 1000, tz=timezone.utc)),
            description=f"Binance deposit {amount} {asset}"
        )
        
        return transaction
    
    def _normalize_withdrawal(self, withdrawal: Dict[str, Any]) -> Transaction:
        """Normalize Binance withdrawal to Transaction model."""
        # Extract information
        asset = withdrawal["coin"]
        amount = Decimal(str(withdrawal["amount"]))
        fee = Decimal(str(withdrawal.get("transactionFee", "0")))
        
        # Get EUR price
        price_eur = self._get_asset_price_eur(asset)
        
        # Create transaction
        transaction = Transaction(
            id=f"binance_withdrawal_{withdrawal['id']}",
            date=datetime.fromisoformat(withdrawal["applyTime"].replace("Z", "+00:00")),
            exchange="binance",
            asset=asset,
            action="transfer",
            amount=-amount,  # Negative for withdrawals
            price_eur=price_eur,
            fee=fee,
            fee_asset=asset,
            tx_id=withdrawal["txId"],
            source="api",
            is_taxable=False,  # Withdrawals are not taxable
            tax_year=self._calculate_tax_year(datetime.fromisoformat(withdrawal["applyTime"].replace("Z", "+00:00"))),
            description=f"Binance withdrawal {amount} {asset}"
        )
        
        return transaction
    
    def _convert_usdt_to_eur(self, usdt_amount: Decimal) -> Decimal:
        """Convert USDT amount to EUR."""
        # For MVP, use a simple conversion rate
        # In production, this should fetch real-time rates
        usdt_to_eur_rate = Decimal("0.85")  # Approximate rate
        return usdt_amount * usdt_to_eur_rate
    
    def _get_asset_price_eur(self, asset: str) -> Decimal:
        """Get asset price in EUR."""
        # For MVP, use hardcoded prices
        # In production, this should fetch real-time prices
        prices = {
            "BTC": Decimal("50000.00"),
            "ETH": Decimal("3000.00"),
            "LTC": Decimal("100.00"),
            "BCH": Decimal("200.00"),
            "XRP": Decimal("0.50"),
        }
        return prices.get(asset.upper(), Decimal("1.00"))
    
    def _calculate_tax_year(self, date: datetime) -> int:
        """Calculate Irish tax year for a date."""
        # Irish tax year runs from April 6th to April 5th
        if date.month >= 4:  # April to December
            return date.year
        else:  # January to March
            return date.year - 1
    
    def sync_transactions(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Sync all transactions from Binance."""
        logger.info(f"Starting Binance sync from {start_date} to {end_date}")
        
        all_transactions = []
        
        try:
            # Get trades
            trades = self.get_trade_history("BTCUSDT", start_date, end_date)
            for trade in trades:
                transaction = self._normalize_trade(trade)
                all_transactions.append(transaction)
            
            # Get deposits
            deposits = self.get_deposit_history(start_date, end_date)
            for deposit in deposits:
                transaction = self._normalize_deposit(deposit)
                all_transactions.append(transaction)
            
            # Get withdrawals
            withdrawals = self.get_withdrawal_history(start_date, end_date)
            for withdrawal in withdrawals:
                transaction = self._normalize_withdrawal(withdrawal)
                all_transactions.append(transaction)
            
            logger.info(f"Synced {len(all_transactions)} transactions from Binance")
            
            return {
                "success": True,
                "transactions": all_transactions,
                "count": len(all_transactions),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Binance sync failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "transactions": [],
                "count": 0
            }
