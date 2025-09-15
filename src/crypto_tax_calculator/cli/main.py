"""
Main CLI entry point for the crypto tax calculator.
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config import create_default_config_file, get_config
from shared.database import init_database, reset_database
from shared.logging_config import setup_logging
from shared.secrets import store_api_credentials, get_api_credentials


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Crypto Capital Gains Tax Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crypto-tax-calc init-db                    # Initialize database
  crypto-tax-calc configure-binance          # Configure Binance API
  crypto-tax-calc sync-binance               # Sync data from Binance
  crypto-tax-calc calculate-cgt --year 2024  # Calculate CGT for 2024
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="crypto-tax-calculator 1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Database commands
    db_parser = subparsers.add_parser("init-db", help="Initialize database")
    db_parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (drop and recreate all tables)"
    )
    
    # Configuration commands
    config_parser = subparsers.add_parser("configure", help="Configure application")
    config_parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create default configuration file"
    )
    
    # Binance commands
    binance_parser = subparsers.add_parser("configure-binance", help="Configure Binance API")
    binance_parser.add_argument("--api-key", required=True, help="Binance API key")
    binance_parser.add_argument("--api-secret", required=True, help="Binance API secret")
    
    # Sync commands
    sync_parser = subparsers.add_parser("sync-binance", help="Sync data from Binance")
    sync_parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    sync_parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    
    # CGT calculation commands
    cgt_parser = subparsers.add_parser("calculate-cgt", help="Calculate CGT")
    cgt_parser.add_argument("--year", type=int, required=True, help="Tax year")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "init-db":
            if args.reset:
                reset_database()
            else:
                init_database()
        
        elif args.command == "configure":
            if args.create_config:
                create_default_config_file()
            else:
                print("Use --create-config to create default configuration file")
        
        elif args.command == "configure-binance":
            store_api_credentials("binance", args.api_key, args.api_secret)
        
        elif args.command == "sync-binance":
            print(f"Syncing Binance data from {args.start_date} to {args.end_date}")
            print("⚠️  This feature will be implemented in Phase 3.3")
        
        elif args.command == "calculate-cgt":
            print(f"Calculating CGT for tax year {args.year}")
            print("⚠️  This feature will be implemented in Phase 3.3")
        
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
