"""
CGT Calculator service for Irish Capital Gains Tax calculations.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional
from collections import defaultdict

from ..models.transaction import Transaction
from ..models.cgt_report import CGTReport
from shared.logging_config import get_logger

logger = get_logger(__name__)


class CGTCalculator:
    """Service for calculating Irish Capital Gains Tax."""
    
    def __init__(self, tax_rate: Decimal = Decimal("0.33"), annual_exemption: Decimal = Decimal("1270")):
        """Initialize CGT calculator."""
        self.tax_rate = tax_rate  # 33%
        self.annual_exemption = annual_exemption  # €1,270
        self.base_currency = "EUR"
    
    def calculate_cgt_for_tax_year(self, transactions: List[Transaction], tax_year: int) -> CGTReport:
        """Calculate CGT for a specific tax year."""
        logger.info(f"Calculating CGT for tax year {tax_year}")
        
        # Filter transactions for the tax year
        tax_year_transactions = [t for t in transactions if t.tax_year == tax_year]
        
        # Separate taxable and non-taxable transactions
        taxable_transactions = [t for t in tax_year_transactions if t.is_taxable]
        
        # Calculate gains and losses by asset
        asset_gains = self._calculate_asset_gains(taxable_transactions)
        
        # Calculate total gains and losses
        total_gains = sum(gains for gains in asset_gains.values() if gains > 0)
        total_losses = sum(abs(gains) for gains in asset_gains.values() if gains < 0)
        net_gains = total_gains - total_losses
        
        # Apply annual exemption
        taxable_gains = max(Decimal("0"), net_gains - self.annual_exemption)
        
        # Calculate tax due
        tax_due = taxable_gains * self.tax_rate
        
        # Create CGT report
        report = CGTReport(
            id=f"cgt_report_{tax_year}",
            tax_year=tax_year,
            total_gains=total_gains,
            total_losses=total_losses,
            net_gains=net_gains,
            annual_exemption=self.annual_exemption,
            taxable_gains=taxable_gains,
            tax_rate=self.tax_rate,
            tax_due=tax_due,
            total_transactions=len(tax_year_transactions),
            taxable_transactions=len(taxable_transactions),
            start_date=datetime(tax_year, 4, 6, tzinfo=timezone.utc),
            end_date=datetime(tax_year + 1, 4, 5, tzinfo=timezone.utc),
            calculation_details={
                "asset_gains": {asset: float(gains) for asset, gains in asset_gains.items()},
                "calculation_method": "FIFO",
                "tax_year_start": f"{tax_year}-04-06",
                "tax_year_end": f"{tax_year + 1}-04-05"
            }
        )
        
        # Calculate the report
        report.calculate_tax()
        
        logger.info(f"CGT calculation complete: {float(tax_due):.2f} EUR tax due")
        
        return report
    
    def _calculate_asset_gains(self, transactions: List[Transaction]) -> Dict[str, Decimal]:
        """Calculate gains/losses for each asset using FIFO method."""
        asset_gains = defaultdict(Decimal)
        
        # Group transactions by asset
        asset_transactions = defaultdict(list)
        for transaction in transactions:
            asset_transactions[transaction.asset].append(transaction)
        
        # Calculate gains for each asset
        for asset, asset_txs in asset_transactions.items():
            gains = self._calculate_fifo_gains(asset_txs)
            asset_gains[asset] = gains
        
        return dict(asset_gains)
    
    def _calculate_fifo_gains(self, transactions: List[Transaction]) -> Decimal:
        """Calculate gains using FIFO method for a single asset."""
        # Sort transactions by date
        sorted_transactions = sorted(transactions, key=lambda t: t.date)
        
        # Separate buys and sells
        buys = [t for t in sorted_transactions if t.is_buy_transaction()]
        sells = [t for t in sorted_transactions if t.is_sell_transaction()]
        
        if not sells:
            return Decimal("0")  # No sells, no gains
        
        total_gains = Decimal("0")
        buy_queue = buys.copy()
        
        for sell in sells:
            sell_amount = abs(sell.amount)
            remaining_sell = sell_amount
            
            while remaining_sell > 0 and buy_queue:
                buy = buy_queue[0]
                buy_amount = buy.amount
                
                if buy_amount <= remaining_sell:
                    # Use entire buy
                    cost_basis = buy_amount * buy.price_eur
                    proceeds = buy_amount * sell.price_eur
                    gain = proceeds - cost_basis
                    total_gains += gain
                    
                    remaining_sell -= buy_amount
                    buy_queue.pop(0)
                else:
                    # Use partial buy
                    cost_basis = remaining_sell * buy.price_eur
                    proceeds = remaining_sell * sell.price_eur
                    gain = proceeds - cost_basis
                    total_gains += gain
                    
                    # Update remaining buy amount
                    buy_queue[0] = Transaction(
                        id=buy.id,
                        date=buy.date,
                        exchange=buy.exchange,
                        asset=buy.asset,
                        action=buy.action,
                        amount=buy_amount - remaining_sell,
                        price_eur=buy.price_eur,
                        fee=buy.fee,
                        fee_asset=buy.fee_asset,
                        tx_id=buy.tx_id,
                        source=buy.source,
                        is_taxable=buy.is_taxable,
                        tax_year=buy.tax_year,
                        description=buy.description
                    )
                    
                    remaining_sell = 0
        
        return total_gains
    
    def calculate_portfolio_summary(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate portfolio summary."""
        # Group by asset
        asset_holdings = defaultdict(Decimal)
        asset_values = defaultdict(Decimal)
        
        for transaction in transactions:
            if transaction.is_taxable:
                asset_holdings[transaction.asset] += transaction.amount
                asset_values[transaction.asset] += transaction.get_eur_value()
        
        # Calculate totals
        total_value = sum(asset_values.values())
        
        # Calculate asset allocation
        asset_allocation = {}
        for asset, value in asset_values.items():
            if total_value > 0:
                allocation = (value / total_value) * 100
                asset_allocation[asset] = float(allocation)
        
        return {
            "total_value_eur": float(total_value),
            "asset_holdings": {asset: float(amount) for asset, amount in asset_holdings.items()},
            "asset_values": {asset: float(value) for asset, value in asset_values.items()},
            "asset_allocation": asset_allocation,
            "total_transactions": len(transactions),
            "taxable_transactions": len([t for t in transactions if t.is_taxable])
        }
    
    def calculate_tax_year_summary(self, transactions: List[Transaction]) -> Dict[int, Dict[str, Any]]:
        """Calculate summary for all tax years."""
        # Group transactions by tax year
        tax_years = defaultdict(list)
        for transaction in transactions:
            if transaction.tax_year:
                tax_years[transaction.tax_year].append(transaction)
        
        # Calculate CGT for each year
        summaries = {}
        for tax_year, year_transactions in tax_years.items():
            cgt_report = self.calculate_cgt_for_tax_year(transactions, tax_year)
            summaries[tax_year] = cgt_report.get_summary()
        
        return summaries
    
    def calculate_loss_carryover(self, transactions: List[Transaction], current_tax_year: int) -> Dict[str, Any]:
        """Calculate loss carryover from previous years."""
        # Get all previous tax years
        tax_years = set(t.tax_year for t in transactions if t.tax_year and t.tax_year < current_tax_year)
        
        total_losses = Decimal("0")
        loss_details = {}
        
        for tax_year in sorted(tax_years):
            year_transactions = [t for t in transactions if t.tax_year == tax_year]
            cgt_report = self.calculate_cgt_for_tax_year(transactions, tax_year)
            
            if cgt_report.net_gains < 0:  # Net loss
                losses = abs(cgt_report.net_gains)
                total_losses += losses
                loss_details[tax_year] = {
                    "net_gains": float(cgt_report.net_gains),
                    "losses": float(losses),
                    "transactions": len(year_transactions)
                }
        
        return {
            "total_loss_carryover": float(total_losses),
            "loss_details": loss_details,
            "can_offset_gains": total_losses > 0
        }
    
    def generate_tax_optimization_tips(self, transactions: List[Transaction], tax_year: int) -> List[str]:
        """Generate tax optimization tips."""
        tips = []
        
        # Calculate current year CGT
        cgt_report = self.calculate_cgt_for_tax_year(transactions, tax_year)
        
        # Check if close to exemption threshold
        if cgt_report.net_gains > 0 and cgt_report.net_gains < self.annual_exemption * 1.1:
            tips.append(f"Consider realizing gains before year-end. You're close to the €{self.annual_exemption} exemption threshold.")
        
        # Check for loss harvesting opportunities
        if cgt_report.net_gains > 0:
            tips.append("Consider selling losing positions to offset gains and reduce tax liability.")
        
        # Check for asset diversification
        asset_counts = defaultdict(int)
        for transaction in transactions:
            if transaction.tax_year == tax_year and transaction.is_taxable:
                asset_counts[transaction.asset] += 1
        
        if len(asset_counts) == 1:
            tips.append("Consider diversifying your crypto portfolio to spread risk and potentially optimize tax timing.")
        
        # Check for frequent trading
        if cgt_report.taxable_transactions > 50:
            tips.append("High transaction frequency may indicate day trading. Consider if this affects your tax status.")
        
        return tips
