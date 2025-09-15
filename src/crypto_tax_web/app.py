"""
Streamlit web application for Crypto Capital Gains Tax Calculator.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import get_session
from shared.secrets import get_api_credentials
from crypto_tax_calculator.services import BinanceService, CSVImporter, CGTCalculator
from crypto_tax_calculator.models import Transaction, CGTReport

# Page configuration
st.set_page_config(
    page_title="Crypto Tax Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit application."""
    st.title("💰 Crypto Capital Gains Tax Calculator")
    st.markdown("Calculate Irish Capital Gains Tax on your cryptocurrency transactions")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page",
            ["Dashboard", "Import Data", "CGT Calculation", "Portfolio", "Transactions"]
        )
    
    # Main content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Import Data":
        show_import_data()
    elif page == "CGT Calculation":
        show_cgt_calculation()
    elif page == "Portfolio":
        show_portfolio()
    elif page == "Transactions":
        show_transactions()

def show_dashboard():
    """Show dashboard page."""
    st.header("📊 Dashboard")
    
    # Get summary statistics
    session = get_session()
    try:
        total_transactions = session.query(Transaction).count()
        total_exchanges = session.query(Transaction.exchange).distinct().count()
        total_assets = session.query(Transaction.asset).distinct().count()
        
        # Get recent transactions
        recent_transactions = session.query(Transaction).order_by(Transaction.date.desc()).limit(5).all()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", total_transactions)
        
        with col2:
            st.metric("Exchanges", total_exchanges)
        
        with col3:
            st.metric("Assets", total_assets)
        
        with col4:
            cgt_reports = session.query(CGTReport).count()
            st.metric("CGT Reports", cgt_reports)
        
        # Recent transactions
        if recent_transactions:
            st.subheader("Recent Transactions")
            df = pd.DataFrame([tx.to_dict() for tx in recent_transactions])
            st.dataframe(df[["date", "exchange", "asset", "action", "amount", "price_eur"]], use_container_width=True)
        else:
            st.info("No transactions found. Import some data to get started!")
            
    finally:
        session.close()

def show_import_data():
    """Show import data page."""
    st.header("📥 Import Data")
    
    # Tabs for different import methods
    tab1, tab2 = st.tabs(["CSV Import", "Binance API"])
    
    with tab1:
        st.subheader("Import CSV File")
        st.markdown("Upload a CSV file from your exchange (Revolut, Coinbase, KuCoin, Kraken)")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Supported formats: Revolut, Coinbase, KuCoin, Kraken"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = Path(f"temp_{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Import CSV
                csv_importer = CSVImporter()
                result = csv_importer.import_csv_file(temp_path)
                
                if result["success"]:
                    st.success(f"✅ Imported {result['count']} transactions from {result['exchange']}")
                    
                    # Save to database
                    session = get_session()
                    try:
                        for transaction in result["transactions"]:
                            session.add(transaction)
                        session.commit()
                        st.success("💾 Transactions saved to database")
                    except Exception as e:
                        st.error(f"❌ Failed to save transactions: {e}")
                        session.rollback()
                    finally:
                        session.close()
                else:
                    st.error(f"❌ Import failed: {result['error']}")
                    
            finally:
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
    
    with tab2:
        st.subheader("Sync from Binance API")
        st.markdown("Sync transactions directly from Binance API")
        
        # Check if API credentials are configured
        api_key, api_secret = get_api_credentials("binance")
        
        if not api_key or not api_secret:
            st.warning("⚠️ Binance API credentials not configured. Please configure them first.")
            st.markdown("Use the CLI command: `crypto-tax-calc configure-binance`")
        else:
            st.success("✅ Binance API credentials configured")
            
            # Date range selection
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime(2024, 1, 1))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now().date())
            
            if st.button("Sync from Binance"):
                with st.spinner("Syncing data from Binance..."):
                    try:
                        # Convert dates to datetime
                        start_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                        end_dt = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
                        
                        # Create Binance service
                        binance_service = BinanceService(api_key, api_secret)
                        
                        # Test connection
                        if not binance_service.test_connection():
                            st.error("❌ Failed to connect to Binance API")
                            return
                        
                        # Sync transactions
                        result = binance_service.sync_transactions(start_dt, end_dt)
                        
                        if result["success"]:
                            st.success(f"✅ Synced {result['count']} transactions from Binance")
                            
                            # Save to database
                            session = get_session()
                            try:
                                for transaction in result["transactions"]:
                                    session.add(transaction)
                                session.commit()
                                st.success("💾 Transactions saved to database")
                            except Exception as e:
                                st.error(f"❌ Failed to save transactions: {e}")
                                session.rollback()
                            finally:
                                session.close()
                        else:
                            st.error(f"❌ Sync failed: {result['error']}")
                            
                    except Exception as e:
                        st.error(f"❌ Error syncing from Binance: {e}")

def show_cgt_calculation():
    """Show CGT calculation page."""
    st.header("🧮 CGT Calculation")
    
    # Tax year selection
    current_year = datetime.now().year
    tax_year = st.selectbox(
        "Select Tax Year",
        range(current_year - 5, current_year + 1),
        index=current_year - current_year + 5  # Default to current year
    )
    
    if st.button("Calculate CGT"):
        with st.spinner("Calculating CGT..."):
            try:
                # Get transactions from database
                session = get_session()
                try:
                    transactions = session.query(Transaction).filter(Transaction.tax_year == tax_year).all()
                    
                    if not transactions:
                        st.warning(f"No transactions found for tax year {tax_year}")
                        return
                    
                    # Calculate CGT
                    cgt_calculator = CGTCalculator()
                    cgt_report = cgt_calculator.calculate_cgt_for_tax_year(transactions, tax_year)
                    
                    # Display results
                    st.subheader(f"CGT Calculation Results for {tax_year}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Total Gains", f"€{cgt_report.total_gains:.2f}")
                        st.metric("Total Losses", f"€{cgt_report.total_losses:.2f}")
                        st.metric("Net Gains", f"€{cgt_report.net_gains:.2f}")
                    
                    with col2:
                        st.metric("Annual Exemption", f"€{cgt_report.annual_exemption:.2f}")
                        st.metric("Taxable Gains", f"€{cgt_report.taxable_gains:.2f}")
                        st.metric("Tax Due", f"€{cgt_report.tax_due:.2f}", delta=f"{cgt_report.tax_rate * 100:.1f}% rate")
                    
                    # Additional info
                    st.info(f"Based on {cgt_report.total_transactions} total transactions ({cgt_report.taxable_transactions} taxable)")
                    
                    # Save report
                    session.add(cgt_report)
                    session.commit()
                    st.success("💾 CGT report saved to database")
                    
                finally:
                    session.close()
                    
            except Exception as e:
                st.error(f"❌ Error calculating CGT: {e}")

def show_portfolio():
    """Show portfolio page."""
    st.header("💼 Portfolio")
    
    # Tax year filter
    tax_year = st.selectbox(
        "Filter by Tax Year",
        ["All"] + list(range(2020, datetime.now().year + 1)),
        index=0
    )
    
    if st.button("Generate Portfolio Summary"):
        with st.spinner("Generating portfolio summary..."):
            try:
                # Get transactions from database
                session = get_session()
                try:
                    query = session.query(Transaction)
                    if tax_year != "All":
                        query = query.filter(Transaction.tax_year == tax_year)
                    
                    transactions = query.all()
                    
                    if not transactions:
                        st.warning("No transactions found")
                        return
                    
                    # Calculate summary
                    cgt_calculator = CGTCalculator()
                    summary = cgt_calculator.calculate_portfolio_summary(transactions)
                    
                    # Display summary
                    st.subheader("Portfolio Summary")
                    if tax_year != "All":
                        st.info(f"Filtered by tax year: {tax_year}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Value", f"€{summary['total_value_eur']:.2f}")
                    
                    with col2:
                        st.metric("Total Transactions", summary['total_transactions'])
                    
                    with col3:
                        st.metric("Taxable Transactions", summary['taxable_transactions'])
                    
                    # Asset holdings
                    st.subheader("Asset Holdings")
                    
                    holdings_data = []
                    for asset, amount in summary['asset_holdings'].items():
                        value = summary['asset_values'][asset]
                        allocation = summary['asset_allocation'][asset]
                        holdings_data.append({
                            "Asset": asset,
                            "Amount": f"{amount:.8f}",
                            "Value (EUR)": f"€{value:.2f}",
                            "Allocation (%)": f"{allocation:.1f}%"
                        })
                    
                    holdings_df = pd.DataFrame(holdings_data)
                    st.dataframe(holdings_df, use_container_width=True)
                    
                    # Asset allocation chart
                    if len(summary['asset_allocation']) > 1:
                        st.subheader("Asset Allocation")
                        allocation_df = pd.DataFrame(
                            list(summary['asset_allocation'].items()),
                            columns=['Asset', 'Allocation']
                        )
                        st.bar_chart(allocation_df.set_index('Asset'))
                    
                finally:
                    session.close()
                    
            except Exception as e:
                st.error(f"❌ Error generating portfolio summary: {e}")

def show_transactions():
    """Show transactions page."""
    st.header("📋 Transactions")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tax_year = st.selectbox(
            "Tax Year",
            ["All"] + list(range(2020, datetime.now().year + 1)),
            index=0
        )
    
    with col2:
        exchange = st.selectbox(
            "Exchange",
            ["All", "binance", "revolut", "coinbase", "kucoin", "kraken"]
        )
    
    with col3:
        asset = st.selectbox(
            "Asset",
            ["All"] + ["BTC", "ETH", "LTC", "BCH", "XRP", "ADA"]
        )
    
    # Limit
    limit = st.slider("Number of transactions to show", 10, 1000, 50)
    
    if st.button("Load Transactions"):
        with st.spinner("Loading transactions..."):
            try:
                # Get transactions from database
                session = get_session()
                try:
                    query = session.query(Transaction)
                    
                    if tax_year != "All":
                        query = query.filter(Transaction.tax_year == tax_year)
                    if exchange != "All":
                        query = query.filter(Transaction.exchange == exchange)
                    if asset != "All":
                        query = query.filter(Transaction.asset == asset)
                    
                    transactions = query.order_by(Transaction.date.desc()).limit(limit).all()
                    
                    if not transactions:
                        st.warning("No transactions found matching the criteria")
                        return
                    
                    # Display transactions
                    st.subheader(f"Transactions ({len(transactions)} shown)")
                    
                    # Convert to DataFrame
                    df = pd.DataFrame([tx.to_dict() for tx in transactions])
                    
                    # Select columns to display
                    display_columns = ["date", "exchange", "asset", "action", "amount", "price_eur", "fee", "tax_year"]
                    df_display = df[display_columns].copy()
                    
                    # Format columns
                    df_display["date"] = pd.to_datetime(df_display["date"]).dt.strftime("%Y-%m-%d")
                    df_display["amount"] = df_display["amount"].apply(lambda x: f"{x:.8f}" if pd.notna(x) else "N/A")
                    df_display["price_eur"] = df_display["price_eur"].apply(lambda x: f"€{x:.2f}" if pd.notna(x) else "N/A")
                    df_display["fee"] = df_display["fee"].apply(lambda x: f"€{x:.2f}" if pd.notna(x) else "N/A")
                    
                    st.dataframe(df_display, use_container_width=True)
                    
                finally:
                    session.close()
                    
            except Exception as e:
                st.error(f"❌ Error loading transactions: {e}")

if __name__ == "__main__":
    main()
