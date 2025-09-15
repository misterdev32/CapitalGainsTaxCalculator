"""
Transaction model for crypto tax calculations.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transaction(Base):
    """Normalized transaction record from all exchanges."""
    
    __tablename__ = "transactions"
    
    # Primary key
    id = Column(String(50), primary_key=True)
    
    # Transaction details
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    asset = Column(String(10), nullable=False, index=True)
    action = Column(String(20), nullable=False, index=True)
    amount = Column(Numeric(20, 8), nullable=False)
    price_eur = Column(Numeric(20, 2), nullable=False)
    fee = Column(Numeric(20, 2), nullable=False, default=0)
    fee_asset = Column(String(10), nullable=False, default="EUR")
    tx_id = Column(String(100), nullable=True, index=True)
    
    # Data source
    source = Column(String(20), nullable=False, default="api")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Tax calculation fields
    is_taxable = Column(Boolean, nullable=False, default=True)
    tax_year = Column(Integer, nullable=True, index=True)
    cost_basis = Column(Numeric(20, 2), nullable=True)
    realized_gain_loss = Column(Numeric(20, 2), nullable=True)
    
    # Additional metadata
    description = Column(Text, nullable=True)
    raw_data = Column(Text, nullable=True)  # JSON string of original data
    
    def __repr__(self):
        return f"<Transaction(id='{self.id}', exchange='{self.exchange}', asset='{self.asset}', action='{self.action}', amount={self.amount})>"
    
    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "exchange": self.exchange,
            "asset": self.asset,
            "action": self.action,
            "amount": float(self.amount) if self.amount else None,
            "price_eur": float(self.price_eur) if self.price_eur else None,
            "fee": float(self.fee) if self.fee else None,
            "fee_asset": self.fee_asset,
            "tx_id": self.tx_id,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_taxable": self.is_taxable,
            "tax_year": self.tax_year,
            "cost_basis": float(self.cost_basis) if self.cost_basis else None,
            "realized_gain_loss": float(self.realized_gain_loss) if self.realized_gain_loss else None,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create transaction from dictionary."""
        # Convert string dates to datetime objects
        if isinstance(data.get("date"), str):
            data["date"] = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        
        # Convert numeric strings to Decimal
        for field in ["amount", "price_eur", "fee", "cost_basis", "realized_gain_loss"]:
            if isinstance(data.get(field), (str, float, int)):
                data[field] = Decimal(str(data[field])) if data[field] is not None else None
        
        return cls(**data)
    
    def calculate_irish_tax_year(self):
        """Calculate Irish tax year for this transaction."""
        if not self.date:
            return None
        
        # Irish tax year runs from April 6th to April 5th
        if self.date.month >= 4:  # April to December
            return self.date.year
        else:  # January to March
            return self.date.year - 1
    
    def is_buy_transaction(self):
        """Check if this is a buy transaction."""
        return self.action in ["buy", "swap"] and self.amount > 0
    
    def is_sell_transaction(self):
        """Check if this is a sell transaction."""
        return self.action in ["sell", "swap"] and self.amount < 0
    
    def is_transfer_transaction(self):
        """Check if this is a transfer transaction."""
        return self.action in ["transfer", "deposit", "withdrawal"]
    
    def get_eur_value(self):
        """Get EUR value of this transaction."""
        return abs(self.amount) * self.price_eur
    
    def get_net_amount_eur(self):
        """Get net amount in EUR (excluding fees)."""
        return self.get_eur_value() - self.fee
