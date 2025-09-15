"""
Exchange model for cryptocurrency exchange metadata.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Exchange(Base):
    """Cryptocurrency exchange metadata and configuration."""
    
    __tablename__ = "exchanges"
    
    # Primary key
    name = Column(String(50), primary_key=True)
    
    # Exchange details
    display_name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # api, csv, manual
    is_active = Column(Boolean, nullable=False, default=True)
    
    # API configuration
    api_key = Column(String(255), nullable=True)
    api_secret = Column(String(255), nullable=True)
    base_url = Column(String(255), nullable=True)
    
    # CSV configuration
    csv_template = Column(JSON, nullable=True)
    csv_encoding = Column(String(20), nullable=True, default="utf-8")
    
    # Exchange capabilities
    supports_api = Column(Boolean, nullable=False, default=False)
    supports_csv = Column(Boolean, nullable=False, default=False)
    supports_real_time = Column(Boolean, nullable=False, default=False)
    
    # Rate limiting
    rate_limit_per_minute = Column(String(20), nullable=True)
    rate_limit_per_day = Column(String(20), nullable=True)
    
    # Metadata
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    supported_assets = Column(JSON, nullable=True)  # List of supported assets
    supported_actions = Column(JSON, nullable=True)  # List of supported actions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Exchange(name='{self.name}', type='{self.type}', active={self.is_active})>"
    
    def to_dict(self):
        """Convert exchange to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "type": self.type,
            "is_active": self.is_active,
            "api_key": self.api_key,
            "api_secret": "***" if self.api_secret else None,  # Hide secret
            "base_url": self.base_url,
            "csv_template": self.csv_template,
            "csv_encoding": self.csv_encoding,
            "supports_api": self.supports_api,
            "supports_csv": self.supports_csv,
            "supports_real_time": self.supports_real_time,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "rate_limit_per_day": self.rate_limit_per_day,
            "website": self.website,
            "description": self.description,
            "supported_assets": self.supported_assets,
            "supported_actions": self.supported_actions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create exchange from dictionary."""
        # Convert string dates to datetime objects
        for field in ["created_at", "updated_at", "last_sync"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field].replace("Z", "+00:00"))
        
        return cls(**data)
    
    def is_api_enabled(self) -> bool:
        """Check if API is enabled and configured."""
        return self.supports_api and self.api_key and self.api_secret
    
    def is_csv_enabled(self) -> bool:
        """Check if CSV import is enabled."""
        return self.supports_csv and self.csv_template is not None
    
    def update_last_sync(self):
        """Update last sync timestamp."""
        self.last_sync = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_sync_status(self) -> str:
        """Get sync status."""
        if not self.last_sync:
            return "never"
        
        age_hours = (datetime.now(timezone.utc) - self.last_sync).total_seconds() / 3600
        
        if age_hours < 1:
            return "recent"
        elif age_hours < 24:
            return "today"
        elif age_hours < 168:  # 7 days
            return "this_week"
        else:
            return "old"
    
    def is_sync_stale(self, max_age_hours: int = 24) -> bool:
        """Check if sync is stale."""
        if not self.last_sync:
            return True
        
        age_hours = (datetime.now(timezone.utc) - self.last_sync).total_seconds() / 3600
        return age_hours > max_age_hours
    
    def get_supported_assets(self) -> list:
        """Get list of supported assets."""
        return self.supported_assets or []
    
    def get_supported_actions(self) -> list:
        """Get list of supported actions."""
        return self.supported_actions or []
    
    def supports_asset(self, asset: str) -> bool:
        """Check if exchange supports specific asset."""
        if not self.supported_assets:
            return True  # Assume all assets supported if not specified
        return asset.upper() in [a.upper() for a in self.supported_assets]
    
    def supports_action(self, action: str) -> bool:
        """Check if exchange supports specific action."""
        if not self.supported_actions:
            return True  # Assume all actions supported if not specified
        return action.lower() in [a.lower() for a in self.supported_actions]
    
    def get_rate_limit_info(self) -> Dict[str, str]:
        """Get rate limit information."""
        return {
            "per_minute": self.rate_limit_per_minute or "unlimited",
            "per_day": self.rate_limit_per_day or "unlimited",
        }
    
    def configure_api(self, api_key: str, api_secret: str, base_url: str = None):
        """Configure API credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        if base_url:
            self.base_url = base_url
        self.updated_at = datetime.now(timezone.utc)
    
    def configure_csv(self, template: dict, encoding: str = "utf-8"):
        """Configure CSV import."""
        self.csv_template = template
        self.csv_encoding = encoding
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self):
        """Deactivate exchange."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
    
    def activate(self):
        """Activate exchange."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)
    
    def get_display_name(self) -> str:
        """Get display name for the exchange."""
        return self.display_name or self.name
    
    def is_configured(self) -> bool:
        """Check if exchange is properly configured."""
        if self.type == "api":
            return self.is_api_enabled()
        elif self.type == "csv":
            return self.is_csv_enabled()
        else:
            return True  # Manual exchanges are always configured
