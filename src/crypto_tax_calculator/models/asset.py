"""
Asset model for cryptocurrency metadata and price history.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Asset(Base):
    """Cryptocurrency asset metadata and price history."""
    
    __tablename__ = "assets"
    
    # Primary key
    symbol = Column(String(10), primary_key=True)
    
    # Asset details
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False, default="cryptocurrency")
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Price information
    current_price_eur = Column(Numeric(20, 2), nullable=True)
    price_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Asset(symbol='{self.symbol}', name='{self.name}', price_eur={self.current_price_eur})>"
    
    def to_dict(self):
        """Convert asset to dictionary."""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "type": self.type,
            "is_active": self.is_active,
            "current_price_eur": float(self.current_price_eur) if self.current_price_eur else None,
            "price_updated_at": self.price_updated_at.isoformat() if self.price_updated_at else None,
            "description": self.description,
            "website": self.website,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create asset from dictionary."""
        # Convert string dates to datetime objects
        if isinstance(data.get("price_updated_at"), str):
            data["price_updated_at"] = datetime.fromisoformat(data["price_updated_at"].replace("Z", "+00:00"))
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        
        # Convert numeric strings to Decimal
        if isinstance(data.get("current_price_eur"), (str, float, int)):
            data["current_price_eur"] = Decimal(str(data["current_price_eur"])) if data["current_price_eur"] is not None else None
        
        return cls(**data)
    
    def update_price(self, price_eur: Decimal):
        """Update current price and timestamp."""
        self.current_price_eur = price_eur
        self.price_updated_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def is_price_stale(self, max_age_hours: int = 24) -> bool:
        """Check if price is stale (older than max_age_hours)."""
        if not self.price_updated_at:
            return True
        
        age_hours = (datetime.now(timezone.utc) - self.price_updated_at).total_seconds() / 3600
        return age_hours > max_age_hours
    
    def get_price_eur(self) -> Optional[Decimal]:
        """Get current price in EUR."""
        return self.current_price_eur
    
    def is_crypto(self) -> bool:
        """Check if this is a cryptocurrency."""
        return self.type == "cryptocurrency"
    
    def is_fiat(self) -> bool:
        """Check if this is a fiat currency."""
        return self.type == "fiat"
    
    def is_stablecoin(self) -> bool:
        """Check if this is a stablecoin."""
        return self.symbol in ["USDT", "USDC", "DAI", "BUSD", "TUSD", "USDP", "FRAX", "LUSD", "SUSD", "GUSD"]
    
    def get_display_name(self) -> str:
        """Get display name for the asset."""
        return f"{self.name} ({self.symbol})" if self.name else self.symbol
