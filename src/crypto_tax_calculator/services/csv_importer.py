"""
CSV importer service for various cryptocurrency exchanges.
"""

import pandas as pd
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import chardet

from ..models.transaction import Transaction
from shared.logging_config import get_logger

logger = get_logger(__name__)


class CSVImporter:
    """Service for importing CSV data from various exchanges."""
    
    def __init__(self):
        """Initialize CSV importer."""
        self.supported_exchanges = ["revolut", "coinbase", "kucoin", "kraken"]
        self.exchange_detectors = {
            "revolut": self._detect_revolut,
            "coinbase": self._detect_coinbase,
            "kucoin": self._detect_kucoin,
            "kraken": self._detect_kraken,
        }
        self.exchange_normalizers = {
            "revolut": self._normalize_revolut,
            "coinbase": self._normalize_coinbase,
            "kucoin": self._normalize_kucoin,
            "kraken": self._normalize_kraken,
        }
    
    def detect_exchange(self, df: pd.DataFrame) -> str:
        """Detect exchange from CSV structure."""
        for exchange, detector in self.exchange_detectors.items():
            if detector(df):
                return exchange
        
        raise ValueError("Unsupported exchange format")
    
    def _detect_revolut(self, df: pd.DataFrame) -> bool:
        """Detect Revolut CSV format."""
        required_columns = ["Type", "Product", "Started Date", "Amount", "Currency"]
        return all(col in df.columns for col in required_columns)
    
    def _detect_coinbase(self, df: pd.DataFrame) -> bool:
        """Detect Coinbase CSV format."""
        required_columns = ["Timestamp", "Transaction Type", "Asset", "Quantity Transacted"]
        return all(col in df.columns for col in required_columns)
    
    def _detect_kucoin(self, df: pd.DataFrame) -> bool:
        """Detect KuCoin CSV format."""
        required_columns = ["UID", "Order Type", "Symbol", "Amount", "Order Price"]
        return all(col in df.columns for col in required_columns)
    
    def _detect_kraken(self, df: pd.DataFrame) -> bool:
        """Detect Kraken CSV format."""
        required_columns = ["txid", "pair", "time", "type", "price", "vol"]
        return all(col in df.columns for col in required_columns)
    
    def import_csv_file(self, file_path: Path) -> Dict[str, Any]:
        """Import CSV file and return transactions."""
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding']
            
            # Read CSV
            df = pd.read_csv(file_path, encoding=encoding)
            
            # Detect exchange
            exchange = self.detect_exchange(df)
            
            # Normalize transactions
            transactions = self.normalize_transactions(df, exchange)
            
            logger.info(f"Imported {len(transactions)} transactions from {exchange}")
            
            return {
                "success": True,
                "exchange": exchange,
                "transactions": transactions,
                "count": len(transactions),
                "encoding": encoding
            }
            
        except Exception as e:
            logger.error(f"CSV import failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "transactions": [],
                "count": 0
            }
    
    def normalize_transactions(self, df: pd.DataFrame, exchange: str) -> List[Transaction]:
        """Normalize transactions for specific exchange."""
        if exchange not in self.exchange_normalizers:
            raise ValueError(f"Unsupported exchange: {exchange}")
        
        normalizer = self.exchange_normalizers[exchange]
        return normalizer(df)
    
    def _normalize_revolut(self, df: pd.DataFrame) -> List[Transaction]:
        """Normalize Revolut transactions."""
        transactions = []
        
        for _, row in df.iterrows():
            try:
                # Skip non-crypto transactions
                if row["Type"] != "EXCHANGE":
                    continue
                
                # Extract basic information
                asset = row["Currency"]
                amount = Decimal(str(row["Amount"]))
                
                # Determine action
                if amount > 0:
                    action = "buy"
                else:
                    action = "sell"
                    amount = -amount  # Make positive for processing
                
                # Calculate price (excluding fees)
                fiat_amount_ex_fees = Decimal(str(row["Fiat amount (ex. fees)"]))
                price_eur = fiat_amount_ex_fees / amount if amount > 0 else Decimal("0")
                
                # Calculate fee
                fee = Decimal(str(row.get("Fee", "0")))
                
                # Parse date
                date_str = row["Started Date"]
                if "T" in date_str:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date = date.replace(tzinfo=timezone.utc)
                
                # Create transaction
                transaction = Transaction(
                    id=f"revolut_{row.name}",
                    date=date,
                    exchange="revolut",
                    asset=asset,
                    action=action,
                    amount=amount if action == "buy" else -amount,
                    price_eur=price_eur,
                    fee=fee,
                    fee_asset="EUR",
                    tx_id=f"revolut_{row.name}",
                    source="csv",
                    is_taxable=True,
                    tax_year=self._calculate_tax_year(date),
                    description=row.get("Description", f"Revolut {action} {amount} {asset}")
                )
                
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"Failed to process Revolut transaction {row.name}: {e}")
                continue
        
        return transactions
    
    def _normalize_coinbase(self, df: pd.DataFrame) -> List[Transaction]:
        """Normalize Coinbase transactions."""
        transactions = []
        
        for _, row in df.iterrows():
            try:
                # Extract basic information
                asset = row["Asset"]
                amount = Decimal(str(row["Quantity Transacted"]))
                
                # Determine action
                action = row["Transaction Type"].lower()
                if action == "sell":
                    amount = -amount  # Negative for sells
                
                # Get price and fee
                price_eur = Decimal(str(row["EUR Spot Price at Transaction"]))
                fee = Decimal(str(row.get("EUR Fees", "0")))
                
                # Parse date
                date_str = row["Timestamp"]
                if "T" in date_str:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date = date.replace(tzinfo=timezone.utc)
                
                # Create transaction
                transaction = Transaction(
                    id=f"coinbase_{row.name}",
                    date=date,
                    exchange="coinbase",
                    asset=asset,
                    action=action,
                    amount=amount,
                    price_eur=price_eur,
                    fee=fee,
                    fee_asset="EUR",
                    tx_id=f"coinbase_{row.name}",
                    source="csv",
                    is_taxable=True,
                    tax_year=self._calculate_tax_year(date),
                    description=row.get("Notes", f"Coinbase {action} {abs(amount)} {asset}")
                )
                
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"Failed to process Coinbase transaction {row.name}: {e}")
                continue
        
        return transactions
    
    def _normalize_kucoin(self, df: pd.DataFrame) -> List[Transaction]:
        """Normalize KuCoin transactions."""
        transactions = []
        
        for _, row in df.iterrows():
            try:
                # Extract basic information
                symbol = row["Symbol"]
                base_asset = symbol.split("-")[0]  # BTC from BTC-USDT
                amount = Decimal(str(row["Amount"]))
                
                # Determine action
                action = row["Order Type"].lower()
                if action == "sell":
                    amount = -amount  # Negative for sells
                
                # Get price (convert from USDT to EUR)
                price_usdt = Decimal(str(row["Order Price"]))
                price_eur = self._convert_usdt_to_eur(price_usdt)
                
                # Get fee
                fee = Decimal(str(row.get("Fee", "0")))
                fee_asset = row.get("Fee Currency", "USDT")
                if fee_asset == "USDT":
                    fee_eur = self._convert_usdt_to_eur(fee)
                else:
                    fee_eur = fee
                
                # Parse date
                date_str = row["Created Time"]
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                date = date.replace(tzinfo=timezone.utc)
                
                # Create transaction
                transaction = Transaction(
                    id=f"kucoin_{row['UID']}",
                    date=date,
                    exchange="kucoin",
                    asset=base_asset,
                    action=action,
                    amount=amount,
                    price_eur=price_eur,
                    fee=fee_eur,
                    fee_asset="EUR",
                    tx_id=row["Order ID"],
                    source="csv",
                    is_taxable=True,
                    tax_year=self._calculate_tax_year(date),
                    description=f"KuCoin {action} {abs(amount)} {base_asset}"
                )
                
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"Failed to process KuCoin transaction {row.get('UID', row.name)}: {e}")
                continue
        
        return transactions
    
    def _normalize_kraken(self, df: pd.DataFrame) -> List[Transaction]:
        """Normalize Kraken transactions."""
        transactions = []
        
        for _, row in df.iterrows():
            try:
                # Extract basic information
                pair = row["pair"]
                base_asset = self._kraken_pair_to_asset(pair)
                amount = Decimal(str(row["vol"]))
                
                # Determine action
                action = row["type"].lower()
                if action == "sell":
                    amount = -amount  # Negative for sells
                
                # Get price and fee
                price_eur = Decimal(str(row["price"]))
                fee = Decimal(str(row.get("fee", "0")))
                
                # Parse date
                timestamp = float(row["time"])
                date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                
                # Create transaction
                transaction = Transaction(
                    id=f"kraken_{row['txid']}",
                    date=date,
                    exchange="kraken",
                    asset=base_asset,
                    action=action,
                    amount=amount,
                    price_eur=price_eur,
                    fee=fee,
                    fee_asset="EUR",
                    tx_id=row["txid"],
                    source="csv",
                    is_taxable=True,
                    tax_year=self._calculate_tax_year(date),
                    description=f"Kraken {action} {abs(amount)} {base_asset}"
                )
                
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"Failed to process Kraken transaction {row.get('txid', row.name)}: {e}")
                continue
        
        return transactions
    
    def _kraken_pair_to_asset(self, pair: str) -> str:
        """Convert Kraken pair to asset symbol."""
        # Remove EUR suffix and XX prefix
        asset = pair.replace("ZEUR", "").replace("XX", "").replace("X", "")
        return asset
    
    def _convert_usdt_to_eur(self, usdt_amount: Decimal) -> Decimal:
        """Convert USDT amount to EUR."""
        # For MVP, use a simple conversion rate
        # In production, this should fetch real-time rates
        usdt_to_eur_rate = Decimal("0.85")  # Approximate rate
        return usdt_amount * usdt_to_eur_rate
    
    def _calculate_tax_year(self, date: datetime) -> int:
        """Calculate Irish tax year for a date."""
        # Irish tax year runs from April 6th to April 5th
        if date.month >= 4:  # April to December
            return date.year
        else:  # January to March
            return date.year - 1
