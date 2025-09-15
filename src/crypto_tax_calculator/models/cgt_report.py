"""
CGT Report model for Irish Capital Gains Tax calculations.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CGTReport(Base):
    """Irish Capital Gains Tax report for a specific tax year."""
    
    __tablename__ = "cgt_reports"
    
    # Primary key
    id = Column(String(50), primary_key=True)
    
    # Report details
    tax_year = Column(Integer, nullable=False, index=True)
    report_type = Column(String(20), nullable=False, default="annual")  # annual, quarterly, custom
    status = Column(String(20), nullable=False, default="draft")  # draft, final, submitted
    
    # Tax calculations
    total_gains = Column(Numeric(20, 2), nullable=False, default=0)
    total_losses = Column(Numeric(20, 2), nullable=False, default=0)
    net_gains = Column(Numeric(20, 2), nullable=False, default=0)
    annual_exemption = Column(Numeric(20, 2), nullable=False, default=1270)  # €1,270
    taxable_gains = Column(Numeric(20, 2), nullable=False, default=0)
    tax_rate = Column(Numeric(5, 4), nullable=False, default=0.33)  # 33%
    tax_due = Column(Numeric(20, 2), nullable=False, default=0)
    
    # Loss carryover
    loss_carryover_used = Column(Numeric(20, 2), nullable=False, default=0)
    loss_carryover_remaining = Column(Numeric(20, 2), nullable=False, default=0)
    
    # Transaction counts
    total_transactions = Column(Integer, nullable=False, default=0)
    taxable_transactions = Column(Integer, nullable=False, default=0)
    
    # Date range
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    calculated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    calculation_details = Column(JSON, nullable=True)  # Detailed breakdown
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<CGTReport(id='{self.id}', tax_year={self.tax_year}, tax_due={self.tax_due})>"
    
    def to_dict(self):
        """Convert CGT report to dictionary."""
        return {
            "id": self.id,
            "tax_year": self.tax_year,
            "report_type": self.report_type,
            "status": self.status,
            "total_gains": float(self.total_gains) if self.total_gains else None,
            "total_losses": float(self.total_losses) if self.total_losses else None,
            "net_gains": float(self.net_gains) if self.net_gains else None,
            "annual_exemption": float(self.annual_exemption) if self.annual_exemption else None,
            "taxable_gains": float(self.taxable_gains) if self.taxable_gains else None,
            "tax_rate": float(self.tax_rate) if self.tax_rate else None,
            "tax_due": float(self.tax_due) if self.tax_due else None,
            "loss_carryover_used": float(self.loss_carryover_used) if self.loss_carryover_used else None,
            "loss_carryover_remaining": float(self.loss_carryover_remaining) if self.loss_carryover_remaining else None,
            "total_transactions": self.total_transactions,
            "taxable_transactions": self.taxable_transactions,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
            "calculation_details": self.calculation_details,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create CGT report from dictionary."""
        # Convert string dates to datetime objects
        for field in ["start_date", "end_date", "created_at", "updated_at", "calculated_at"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field].replace("Z", "+00:00"))
        
        # Convert numeric strings to Decimal
        for field in ["total_gains", "total_losses", "net_gains", "annual_exemption", 
                     "taxable_gains", "tax_rate", "tax_due", "loss_carryover_used", "loss_carryover_remaining"]:
            if isinstance(data.get(field), (str, float, int)):
                data[field] = Decimal(str(data[field])) if data[field] is not None else None
        
        return cls(**data)
    
    def calculate_tax(self):
        """Calculate tax based on current values."""
        # Calculate net gains
        self.net_gains = self.total_gains - self.total_losses
        
        # Apply loss carryover
        if self.net_gains > 0 and self.loss_carryover_remaining > 0:
            carryover_to_use = min(self.loss_carryover_remaining, self.net_gains)
            self.loss_carryover_used = carryover_to_use
            self.taxable_gains = self.net_gains - carryover_to_use
            self.loss_carryover_remaining = self.loss_carryover_remaining - carryover_to_use
        else:
            self.taxable_gains = max(0, self.net_gains)
        
        # Apply annual exemption
        if self.taxable_gains > 0:
            self.taxable_gains = max(0, self.taxable_gains - self.annual_exemption)
        
        # Calculate tax due
        self.tax_due = self.taxable_gains * self.tax_rate
        
        # Update calculation timestamp
        self.calculated_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def is_final(self) -> bool:
        """Check if report is final."""
        return self.status == "final"
    
    def is_submitted(self) -> bool:
        """Check if report is submitted."""
        return self.status == "submitted"
    
    def mark_as_final(self):
        """Mark report as final."""
        self.status = "final"
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_as_submitted(self):
        """Mark report as submitted."""
        self.status = "submitted"
        self.updated_at = datetime.now(timezone.utc)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of the report."""
        return {
            "tax_year": self.tax_year,
            "net_gains": float(self.net_gains) if self.net_gains else 0,
            "taxable_gains": float(self.taxable_gains) if self.taxable_gains else 0,
            "tax_due": float(self.tax_due) if self.tax_due else 0,
            "status": self.status,
            "total_transactions": self.total_transactions,
            "taxable_transactions": self.taxable_transactions,
        }
    
    def add_calculation_detail(self, key: str, value: Any):
        """Add calculation detail."""
        if self.calculation_details is None:
            self.calculation_details = {}
        self.calculation_details[key] = value
    
    def get_calculation_detail(self, key: str, default: Any = None) -> Any:
        """Get calculation detail."""
        if self.calculation_details is None:
            return default
        return self.calculation_details.get(key, default)
    
    def has_tax_liability(self) -> bool:
        """Check if there is a tax liability."""
        return self.tax_due > 0
    
    def get_tax_savings_from_exemption(self) -> Decimal:
        """Get tax savings from annual exemption."""
        if self.taxable_gains <= 0:
            return Decimal("0")
        
        # Calculate how much of the exemption was used
        exemption_used = min(self.annual_exemption, self.net_gains)
        return exemption_used * self.tax_rate
