"""
Contract tests for CSV template functionality.

These tests define the expected behavior for CSV template generation,
validation, and management before implementation.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch

from crypto_tax_calculator.services.csv_template_manager import CSVTemplateManager


class TestCSVTemplates:
    """Contract tests for CSV template functionality."""
    
    @pytest.fixture
    def template_manager(self):
        """Create a CSV template manager instance for testing."""
        return CSVTemplateManager()
    
    @pytest.fixture
    def sample_revolut_template(self):
        """Sample Revolut CSV template."""
        return {
            "exchange": "revolut",
            "version": "1.0",
            "description": "Revolut cryptocurrency transaction export template",
            "required_columns": [
                "Type",
                "Product", 
                "Started Date",
                "Completed Date",
                "Description",
                "Amount",
                "Currency",
                "Fiat amount (inc. fees)",
                "Fiat amount (ex. fees)",
                "Fee",
                "Base currency",
                "State"
            ],
            "optional_columns": [
                "Description",
                "Completed Date"
            ],
            "data_types": {
                "Type": "string",
                "Product": "string",
                "Started Date": "datetime",
                "Amount": "decimal",
                "Currency": "string",
                "Fiat amount (inc. fees)": "decimal",
                "Fiat amount (ex. fees)": "decimal",
                "Fee": "decimal",
                "Base currency": "string",
                "State": "string"
            },
            "validation_rules": {
                "Type": ["EXCHANGE", "TRANSFER", "CASHBACK"],
                "Currency": ["BTC", "ETH", "LTC", "BCH", "XRP"],
                "Base currency": ["EUR", "USD", "GBP"],
                "State": ["COMPLETED", "PENDING", "FAILED"]
            },
            "sample_data": [
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
            ]
        }
    
    @pytest.fixture
    def sample_coinbase_template(self):
        """Sample Coinbase CSV template."""
        return {
            "exchange": "coinbase",
            "version": "1.0",
            "description": "Coinbase Pro transaction export template",
            "required_columns": [
                "Timestamp",
                "Transaction Type",
                "Asset",
                "Quantity Transacted",
                "EUR Spot Price at Transaction",
                "EUR Sub Total",
                "EUR Total (inclusive of fees)",
                "EUR Fees",
                "Notes"
            ],
            "optional_columns": [
                "Notes"
            ],
            "data_types": {
                "Timestamp": "datetime",
                "Transaction Type": "string",
                "Asset": "string",
                "Quantity Transacted": "decimal",
                "EUR Spot Price at Transaction": "decimal",
                "EUR Sub Total": "decimal",
                "EUR Total (inclusive of fees)": "decimal",
                "EUR Fees": "decimal",
                "Notes": "string"
            },
            "validation_rules": {
                "Transaction Type": ["Buy", "Sell", "Send", "Receive"],
                "Asset": ["BTC", "ETH", "LTC", "BCH", "XRP", "ADA"]
            },
            "sample_data": [
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
            ]
        }

    def test_template_manager_initialization(self, template_manager):
        """Test CSV template manager initialization."""
        assert template_manager.supported_exchanges == ["revolut", "coinbase", "kucoin", "kraken"]
        assert template_manager.templates is not None
        assert template_manager.template_versions is not None

    def test_get_template_revolut(self, template_manager, sample_revolut_template):
        """Test getting Revolut CSV template."""
        with patch.object(template_manager, 'templates') as mock_templates:
            mock_templates.get.return_value = sample_revolut_template
            
            template = template_manager.get_template("revolut")
            
            assert template["exchange"] == "revolut"
            assert template["version"] == "1.0"
            assert len(template["required_columns"]) == 12
            assert "Type" in template["required_columns"]
            assert "Amount" in template["required_columns"]
            assert "Currency" in template["required_columns"]

    def test_get_template_coinbase(self, template_manager, sample_coinbase_template):
        """Test getting Coinbase CSV template."""
        with patch.object(template_manager, 'templates') as mock_templates:
            mock_templates.get.return_value = sample_coinbase_template
            
            template = template_manager.get_template("coinbase")
            
            assert template["exchange"] == "coinbase"
            assert template["version"] == "1.0"
            assert len(template["required_columns"]) == 9
            assert "Timestamp" in template["required_columns"]
            assert "Transaction Type" in template["required_columns"]
            assert "Asset" in template["required_columns"]

    def test_get_template_unsupported_exchange(self, template_manager):
        """Test getting template for unsupported exchange."""
        with pytest.raises(ValueError, match="Unsupported exchange"):
            template_manager.get_template("unsupported_exchange")

    def test_get_template_version(self, template_manager, sample_revolut_template):
        """Test getting specific template version."""
        with patch.object(template_manager, 'templates') as mock_templates:
            mock_templates.get.return_value = sample_revolut_template
            
            template = template_manager.get_template("revolut", version="1.0")
            
            assert template["version"] == "1.0"

    def test_get_template_latest_version(self, template_manager, sample_revolut_template):
        """Test getting latest template version."""
        with patch.object(template_manager, 'templates') as mock_templates:
            mock_templates.get.return_value = sample_revolut_template
            
            template = template_manager.get_template("revolut", version="latest")
            
            assert template["version"] == "1.0"

    def test_generate_sample_csv_revolut(self, template_manager, sample_revolut_template):
        """Test generating sample CSV for Revolut."""
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            sample_csv = template_manager.generate_sample_csv("revolut")
            
            assert isinstance(sample_csv, pd.DataFrame)
            assert len(sample_csv) == 1  # One sample row
            assert list(sample_csv.columns) == sample_revolut_template["required_columns"]
            assert sample_csv.iloc[0]["Type"] == "EXCHANGE"
            assert sample_csv.iloc[0]["Currency"] == "BTC"

    def test_generate_sample_csv_coinbase(self, template_manager, sample_coinbase_template):
        """Test generating sample CSV for Coinbase."""
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_coinbase_template
            
            sample_csv = template_manager.generate_sample_csv("coinbase")
            
            assert isinstance(sample_csv, pd.DataFrame)
            assert len(sample_csv) == 1  # One sample row
            assert list(sample_csv.columns) == sample_coinbase_template["required_columns"]
            assert sample_csv.iloc[0]["Transaction Type"] == "Buy"
            assert sample_csv.iloc[0]["Asset"] == "BTC"

    def test_generate_sample_csv_with_multiple_rows(self, template_manager, sample_revolut_template):
        """Test generating sample CSV with multiple rows."""
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            sample_csv = template_manager.generate_sample_csv("revolut", num_rows=3)
            
            assert isinstance(sample_csv, pd.DataFrame)
            assert len(sample_csv) == 3
            assert list(sample_csv.columns) == sample_revolut_template["required_columns"]

    def test_validate_csv_against_template(self, template_manager, sample_revolut_template):
        """Test validating CSV against template."""
        # Valid CSV data
        valid_csv = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
        ])
        
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            is_valid, errors = template_manager.validate_csv_against_template(valid_csv, "revolut")
            
            assert is_valid is True
            assert len(errors) == 0

    def test_validate_csv_against_template_missing_columns(self, template_manager, sample_revolut_template):
        """Test validating CSV with missing columns against template."""
        # CSV with missing required columns
        invalid_csv = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin"
                # Missing required columns
            }
        ])
        
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            is_valid, errors = template_manager.validate_csv_against_template(invalid_csv, "revolut")
            
            assert is_valid is False
            assert len(errors) > 0
            assert any("missing required column" in error.lower() for error in errors)

    def test_validate_csv_against_template_wrong_data_types(self, template_manager, sample_revolut_template):
        """Test validating CSV with wrong data types against template."""
        # CSV with wrong data types
        invalid_csv = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "invalid_date",
                "Amount": "not_a_number",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "invalid_fee",
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
        ])
        
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            is_valid, errors = template_manager.validate_csv_against_template(invalid_csv, "revolut")
            
            assert is_valid is False
            assert len(errors) > 0
            assert any("invalid data type" in error.lower() for error in errors)

    def test_validate_csv_against_template_invalid_values(self, template_manager, sample_revolut_template):
        """Test validating CSV with invalid values against template."""
        # CSV with invalid values
        invalid_csv = pd.DataFrame([
            {
                "Type": "INVALID_TYPE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "INVALID_CURRENCY",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "INVALID_BASE",
                "State": "INVALID_STATE"
            }
        ])
        
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            is_valid, errors = template_manager.validate_csv_against_template(invalid_csv, "revolut")
            
            assert is_valid is False
            assert len(errors) > 0
            assert any("invalid value" in error.lower() for error in errors)

    def test_get_template_versions(self, template_manager):
        """Test getting available template versions for an exchange."""
        with patch.object(template_manager, 'template_versions') as mock_versions:
            mock_versions.get.return_value = ["1.0", "1.1", "2.0"]
            
            versions = template_manager.get_template_versions("revolut")
            
            assert versions == ["1.0", "1.1", "2.0"]

    def test_get_latest_template_version(self, template_manager):
        """Test getting latest template version for an exchange."""
        with patch.object(template_manager, 'template_versions') as mock_versions:
            mock_versions.get.return_value = ["1.0", "1.1", "2.0"]
            
            latest_version = template_manager.get_latest_template_version("revolut")
            
            assert latest_version == "2.0"

    def test_compare_template_versions(self, template_manager):
        """Test comparing different template versions."""
        template_v1 = {
            "exchange": "revolut",
            "version": "1.0",
            "required_columns": ["Type", "Amount", "Currency"]
        }
        
        template_v2 = {
            "exchange": "revolut", 
            "version": "2.0",
            "required_columns": ["Type", "Amount", "Currency", "Fee"]
        }
        
        differences = template_manager.compare_template_versions(template_v1, template_v2)
        
        assert "added_columns" in differences
        assert "removed_columns" in differences
        assert "Fee" in differences["added_columns"]
        assert len(differences["removed_columns"]) == 0

    def test_generate_template_documentation(self, template_manager, sample_revolut_template):
        """Test generating template documentation."""
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            documentation = template_manager.generate_template_documentation("revolut")
            
            assert "exchange" in documentation
            assert "version" in documentation
            assert "description" in documentation
            assert "required_columns" in documentation
            assert "data_types" in documentation
            assert "validation_rules" in documentation
            assert "sample_data" in documentation

    def test_export_template_to_file(self, template_manager, sample_revolut_template, tmp_path):
        """Test exporting template to file."""
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            output_file = tmp_path / "revolut_template.json"
            template_manager.export_template_to_file("revolut", output_file)
            
            assert output_file.exists()
            assert output_file.stat().st_size > 0

    def test_import_template_from_file(self, template_manager, sample_revolut_template, tmp_path):
        """Test importing template from file."""
        import json
        
        template_file = tmp_path / "revolut_template.json"
        with open(template_file, 'w') as f:
            json.dump(sample_revolut_template, f)
        
        imported_template = template_manager.import_template_from_file(template_file)
        
        assert imported_template["exchange"] == "revolut"
        assert imported_template["version"] == "1.0"
        assert len(imported_template["required_columns"]) == 12

    def test_create_custom_template(self, template_manager):
        """Test creating custom template."""
        custom_template = {
            "exchange": "custom_exchange",
            "version": "1.0",
            "description": "Custom exchange template",
            "required_columns": ["Date", "Amount", "Currency"],
            "data_types": {
                "Date": "datetime",
                "Amount": "decimal",
                "Currency": "string"
            }
        }
        
        template_manager.create_custom_template("custom_exchange", custom_template)
        
        # Verify template was created
        stored_template = template_manager.get_template("custom_exchange")
        assert stored_template["exchange"] == "custom_exchange"
        assert stored_template["version"] == "1.0"

    def test_update_template(self, template_manager, sample_revolut_template):
        """Test updating existing template."""
        # Create initial template
        template_manager.create_custom_template("revolut", sample_revolut_template)
        
        # Update template
        updated_template = sample_revolut_template.copy()
        updated_template["version"] = "1.1"
        updated_template["required_columns"].append("New Column")
        
        template_manager.update_template("revolut", updated_template)
        
        # Verify template was updated
        stored_template = template_manager.get_template("revolut")
        assert stored_template["version"] == "1.1"
        assert "New Column" in stored_template["required_columns"]

    def test_delete_template(self, template_manager, sample_revolut_template):
        """Test deleting template."""
        # Create template
        template_manager.create_custom_template("revolut", sample_revolut_template)
        
        # Verify template exists
        template = template_manager.get_template("revolut")
        assert template is not None
        
        # Delete template
        template_manager.delete_template("revolut")
        
        # Verify template was deleted
        with pytest.raises(ValueError):
            template_manager.get_template("revolut")

    def test_list_available_templates(self, template_manager):
        """Test listing available templates."""
        with patch.object(template_manager, 'templates') as mock_templates:
            mock_templates.keys.return_value = ["revolut", "coinbase", "kucoin", "kraken"]
            
            available_templates = template_manager.list_available_templates()
            
            assert "revolut" in available_templates
            assert "coinbase" in available_templates
            assert "kucoin" in available_templates
            assert "kraken" in available_templates

    def test_validate_template_structure(self, template_manager):
        """Test validating template structure."""
        # Valid template
        valid_template = {
            "exchange": "test_exchange",
            "version": "1.0",
            "description": "Test template",
            "required_columns": ["Column1", "Column2"],
            "data_types": {"Column1": "string", "Column2": "decimal"},
            "validation_rules": {"Column1": ["value1", "value2"]},
            "sample_data": [{"Column1": "value1", "Column2": "1.0"}]
        }
        
        is_valid, errors = template_manager.validate_template_structure(valid_template)
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid template (missing required fields)
        invalid_template = {
            "exchange": "test_exchange"
            # Missing required fields
        }
        
        is_valid, errors = template_manager.validate_template_structure(invalid_template)
        assert is_valid is False
        assert len(errors) > 0
        assert any("missing required field" in error.lower() for error in errors)

    def test_generate_template_schema(self, template_manager, sample_revolut_template):
        """Test generating JSON schema for template."""
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            schema = template_manager.generate_template_schema("revolut")
            
            assert "type" in schema
            assert "properties" in schema
            assert "required" in schema
            assert schema["type"] == "object"
            assert "Type" in schema["properties"]
            assert "Amount" in schema["properties"]

    def test_validate_csv_against_schema(self, template_manager, sample_revolut_template):
        """Test validating CSV against JSON schema."""
        # Valid CSV data
        valid_csv = pd.DataFrame([
            {
                "Type": "EXCHANGE",
                "Product": "Bitcoin",
                "Started Date": "2022-01-01 12:00:00",
                "Amount": "0.001",
                "Currency": "BTC",
                "Fiat amount (inc. fees)": "50.00",
                "Fiat amount (ex. fees)": "49.50",
                "Fee": "0.50",
                "Base currency": "EUR",
                "State": "COMPLETED"
            }
        ])
        
        with patch.object(template_manager, 'get_template') as mock_get_template:
            mock_get_template.return_value = sample_revolut_template
            
            is_valid, errors = template_manager.validate_csv_against_schema(valid_csv, "revolut")
            
            assert is_valid is True
            assert len(errors) == 0
