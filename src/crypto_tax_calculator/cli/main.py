"""
Main CLI entry point for the crypto tax calculator.
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config import create_default_config_file, get_config
from shared.database import init_database, reset_database, get_session
from shared.logging_config import setup_logging
from shared.secrets import store_api_credentials, get_api_credentials
from crypto_tax_calculator.services import BinanceService, CSVImporter, CGTCalculator
from crypto_tax_calculator.models import Transaction, CGTReport


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
    
    # CSV import commands
    csv_parser = subparsers.add_parser("import-csv", help="Import CSV file")
    csv_parser.add_argument("--file", required=True, help="CSV file path")
    csv_parser.add_argument("--exchange", help="Exchange name (auto-detected if not specified)")
    
    # CGT calculation commands
    cgt_parser = subparsers.add_parser("calculate-cgt", help="Calculate CGT")
    cgt_parser.add_argument("--year", type=int, required=True, help="Tax year")
    
    # Portfolio commands
    portfolio_parser = subparsers.add_parser("portfolio-summary", help="Show portfolio summary")
    portfolio_parser.add_argument("--year", type=int, help="Filter by tax year")
    
    # List commands
    list_parser = subparsers.add_parser("list-transactions", help="List transactions")
    list_parser.add_argument("--year", type=int, help="Filter by tax year")
    list_parser.add_argument("--exchange", help="Filter by exchange")
    list_parser.add_argument("--asset", help="Filter by asset")
    list_parser.add_argument("--limit", type=int, default=50, help="Limit number of results")
    
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
            sync_binance_data(args.start_date, args.end_date)
        
        elif args.command == "import-csv":
            import_csv_file(args.file, args.exchange)
        
        elif args.command == "calculate-cgt":
            calculate_cgt(args.year)
        
        elif args.command == "portfolio-summary":
            show_portfolio_summary(args.year)
        
        elif args.command == "list-transactions":
            list_transactions(args.year, args.exchange, args.asset, args.limit)
        
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def sync_binance_data(start_date: str, end_date: str):
    """Sync data from Binance."""
    try:
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        
        # Get API credentials
        api_key, api_secret = get_api_credentials("binance")
        if not api_key or not api_secret:
            print("❌ Binance API credentials not configured. Use 'configure-binance' first.")
            return
        
        # Create Binance service
        binance_service = BinanceService(api_key, api_secret)
        
        # Test connection
        if not binance_service.test_connection():
            print("❌ Failed to connect to Binance API")
            return
        
        print(f"🔄 Syncing Binance data from {start_date} to {end_date}...")
        
        # Sync transactions
        result = binance_service.sync_transactions(start_dt, end_dt)
        
        if result["success"]:
            print(f"✅ Synced {result['count']} transactions from Binance")
            
            # Save to database
            session = get_session()
            try:
                for transaction in result["transactions"]:
                    session.add(transaction)
                session.commit()
                print("💾 Transactions saved to database")
            except Exception as e:
                print(f"❌ Failed to save transactions: {e}")
                session.rollback()
            finally:
                session.close()
        else:
            print(f"❌ Sync failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error syncing Binance data: {e}")


def import_csv_file(file_path: str, exchange: str = None):
    """Import CSV file."""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"🔄 Importing CSV file: {file_path}")
        
        # Create CSV importer
        csv_importer = CSVImporter()
        
        # Import file
        result = csv_importer.import_csv_file(file_path)
        
        if result["success"]:
            print(f"✅ Imported {result['count']} transactions from {result['exchange']}")
            
            # Save to database
            session = get_session()
            try:
                for transaction in result["transactions"]:
                    session.add(transaction)
                session.commit()
                print("💾 Transactions saved to database")
            except Exception as e:
                print(f"❌ Failed to save transactions: {e}")
                session.rollback()
            finally:
                session.close()
        else:
            print(f"❌ Import failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error importing CSV: {e}")


def calculate_cgt(tax_year: int):
    """Calculate CGT for a tax year."""
    try:
        print(f"🔄 Calculating CGT for tax year {tax_year}...")
        
        # Get transactions from database
        session = get_session()
        try:
            transactions = session.query(Transaction).filter(Transaction.tax_year == tax_year).all()
            
            if not transactions:
                print(f"❌ No transactions found for tax year {tax_year}")
                return
            
            print(f"📊 Found {len(transactions)} transactions for tax year {tax_year}")
            
            # Calculate CGT
            cgt_calculator = CGTCalculator()
            cgt_report = cgt_calculator.calculate_cgt_for_tax_year(transactions, tax_year)
            
            # Display results
            print("\n📋 CGT Calculation Results:")
            print(f"Tax Year: {cgt_report.tax_year}")
            print(f"Total Gains: €{cgt_report.total_gains:.2f}")
            print(f"Total Losses: €{cgt_report.total_losses:.2f}")
            print(f"Net Gains: €{cgt_report.net_gains:.2f}")
            print(f"Annual Exemption: €{cgt_report.annual_exemption:.2f}")
            print(f"Taxable Gains: €{cgt_report.taxable_gains:.2f}")
            print(f"Tax Rate: {cgt_report.tax_rate * 100:.1f}%")
            print(f"Tax Due: €{cgt_report.tax_due:.2f}")
            print(f"Total Transactions: {cgt_report.total_transactions}")
            print(f"Taxable Transactions: {cgt_report.taxable_transactions}")
            
            # Save report
            session.add(cgt_report)
            session.commit()
            print("\n💾 CGT report saved to database")
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Error calculating CGT: {e}")


def show_portfolio_summary(tax_year: int = None):
    """Show portfolio summary."""
    try:
        print("🔄 Generating portfolio summary...")
        
        # Get transactions from database
        session = get_session()
        try:
            query = session.query(Transaction)
            if tax_year:
                query = query.filter(Transaction.tax_year == tax_year)
            
            transactions = query.all()
            
            if not transactions:
                print("❌ No transactions found")
                return
            
            # Calculate summary
            cgt_calculator = CGTCalculator()
            summary = cgt_calculator.calculate_portfolio_summary(transactions)
            
            # Display results
            print("\n📊 Portfolio Summary:")
            if tax_year:
                print(f"Tax Year: {tax_year}")
            print(f"Total Value: €{summary['total_value_eur']:.2f}")
            print(f"Total Transactions: {summary['total_transactions']}")
            print(f"Taxable Transactions: {summary['taxable_transactions']}")
            
            print("\n💰 Asset Holdings:")
            for asset, amount in summary['asset_holdings'].items():
                value = summary['asset_values'][asset]
                allocation = summary['asset_allocation'][asset]
                print(f"  {asset}: {amount:.8f} (€{value:.2f}, {allocation:.1f}%)")
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Error generating portfolio summary: {e}")


def list_transactions(tax_year: int = None, exchange: str = None, asset: str = None, limit: int = 50):
    """List transactions."""
    try:
        print("🔄 Fetching transactions...")
        
        # Get transactions from database
        session = get_session()
        try:
            query = session.query(Transaction)
            
            if tax_year:
                query = query.filter(Transaction.tax_year == tax_year)
            if exchange:
                query = query.filter(Transaction.exchange == exchange)
            if asset:
                query = query.filter(Transaction.asset == asset)
            
            transactions = query.order_by(Transaction.date.desc()).limit(limit).all()
            
            if not transactions:
                print("❌ No transactions found")
                return
            
            # Display results
            print(f"\n📋 Transactions (showing {len(transactions)} of {limit}):")
            print(f"{'Date':<12} {'Exchange':<10} {'Asset':<8} {'Action':<8} {'Amount':<15} {'Price':<12} {'Tax Year':<8}")
            print("-" * 80)
            
            for tx in transactions:
                date_str = tx.date.strftime("%Y-%m-%d") if tx.date else "N/A"
                amount_str = f"{tx.amount:.8f}" if tx.amount else "N/A"
                price_str = f"€{tx.price_eur:.2f}" if tx.price_eur else "N/A"
                tax_year_str = str(tx.tax_year) if tx.tax_year else "N/A"
                
                print(f"{date_str:<12} {tx.exchange:<10} {tx.asset:<8} {tx.action:<8} {amount_str:<15} {price_str:<12} {tax_year_str:<8}")
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Error listing transactions: {e}")


if __name__ == "__main__":
    main()
