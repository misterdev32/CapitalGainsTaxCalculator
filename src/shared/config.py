"""
Configuration management for the application.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def get_config() -> Dict[str, Any]:
    """Get application configuration."""
    config_file = Path("config.yaml")
    
    # Default configuration
    default_config = {
        "database": {
            "type": "sqlite",  # sqlite or postgresql
            "path": "data/crypto_tax_calc.db",
            "host": "localhost",
            "port": 5432,
            "database": "crypto_tax_calc",
            "username": "postgres",
            "password": "",
            "echo": False,
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "file": "logs/crypto_tax_calc.log",
            "max_size": "10MB",
            "backup_count": 5,
        },
        "binance": {
            "api_key": "",
            "api_secret": "",
            "base_url": "https://api.binance.com",
            "rate_limit": 1200,  # requests per minute
            "timeout": 30,
        },
        "exchanges": {
            "revolut": {
                "type": "csv",
                "enabled": True,
            },
            "coinbase": {
                "type": "csv",
                "enabled": True,
            },
            "kucoin": {
                "type": "csv",
                "enabled": True,
            },
            "kraken": {
                "type": "csv",
                "enabled": True,
            },
        },
        "cgt": {
            "tax_rate": 0.33,  # 33%
            "annual_exemption": 1270,  # €1,270
            "base_currency": "EUR",
            "tax_year_start_month": 4,  # April
            "tax_year_start_day": 6,    # 6th
        },
        "data": {
            "snapshots_dir": "data/snapshots",
            "csv_exports_dir": "data/csv_exports",
            "reports_dir": "data/reports",
            "backup_retention_days": 365,
        },
        "web": {
            "host": "localhost",
            "port": 8501,
            "debug": False,
        },
    }
    
    # Load from file if exists
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                file_config = yaml.safe_load(f) or {}
            # Merge with defaults
            config = _merge_config(default_config, file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            config = default_config
    else:
        config = default_config
    
    # Override with environment variables
    config = _apply_env_overrides(config)
    
    return config


def _merge_config(default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge configuration dictionaries."""
    result = default.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_config(result[key], value)
        else:
            result[key] = value
    
    return result


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration."""
    env_mappings = {
        "CRYPTO_TAX_DB_TYPE": ("database", "type"),
        "CRYPTO_TAX_DB_PATH": ("database", "path"),
        "CRYPTO_TAX_DB_HOST": ("database", "host"),
        "CRYPTO_TAX_DB_PORT": ("database", "port"),
        "CRYPTO_TAX_DB_NAME": ("database", "database"),
        "CRYPTO_TAX_DB_USER": ("database", "username"),
        "CRYPTO_TAX_DB_PASSWORD": ("database", "password"),
        "CRYPTO_TAX_BINANCE_API_KEY": ("binance", "api_key"),
        "CRYPTO_TAX_BINANCE_API_SECRET": ("binance", "api_secret"),
        "CRYPTO_TAX_LOG_LEVEL": ("logging", "level"),
        "CRYPTO_TAX_LOG_FILE": ("logging", "file"),
        "CRYPTO_TAX_WEB_HOST": ("web", "host"),
        "CRYPTO_TAX_WEB_PORT": ("web", "port"),
    }
    
    for env_var, (section, key) in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            # Convert numeric values
            if key in ["port", "rate_limit", "timeout", "backup_retention_days"]:
                try:
                    value = int(value)
                except ValueError:
                    pass
            elif key in ["tax_rate"]:
                try:
                    value = float(value)
                except ValueError:
                    pass
            elif key in ["echo", "debug", "enabled"]:
                value = value.lower() in ("true", "1", "yes", "on")
            
            config[section][key] = value
    
    return config


def save_config(config: Dict[str, Any], config_file: Optional[Path] = None) -> None:
    """Save configuration to file."""
    if config_file is None:
        config_file = Path("config.yaml")
    
    # Ensure directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"✅ Configuration saved to {config_file}")


def create_default_config_file() -> None:
    """Create a default configuration file."""
    config = get_config()
    save_config(config)
    print("✅ Default configuration file created: config.yaml")
