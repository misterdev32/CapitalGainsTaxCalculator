"""
Main CLI entry point for the crypto tax web dashboard.
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config import get_config
from shared.logging_config import setup_logging


def main():
    """Main web CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Crypto Tax Calculator Web Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crypto-tax-web start-dashboard              # Start web dashboard
  crypto-tax-web start-dashboard --port 8502  # Start on custom port
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="crypto-tax-web 1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("start-dashboard", help="Start web dashboard")
    dashboard_parser.add_argument("--host", default="localhost", help="Host to bind to")
    dashboard_parser.add_argument("--port", type=int, default=8501, help="Port to bind to")
    dashboard_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "start-dashboard":
            print(f"Starting web dashboard on {args.host}:{args.port}")
            print("⚠️  This feature will be implemented in Phase 3.4")
            print(f"Dashboard will be available at: http://{args.host}:{args.port}")
        
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
