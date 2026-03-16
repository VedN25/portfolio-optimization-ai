"""
Streamlit Dashboard for Portfolio Optimization

This module provides an interactive dashboard for portfolio optimization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time

# Configure page
st.set_page_config(
    page_title="Portfolio Optimization AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Portfolio Optimization AI</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # Input method
        input_method = st.selectbox(
            "Input Method",
            ["Manual Entry", "Predefined Portfolios"]
        )
        
        if input_method == "Manual Entry":
            tickers = get_manual_tickers()
        else:
            tickers = get_predefined_portfolios()
        
        # Optimization parameters
        st.subheader("Optimization Parameters")
        
        optimization_method = st.selectbox(
            "Optimization Method",
            ["max_sharpe", "min_volatility", "equal_weight"],
            help="Choose the optimization strategy"
        )
        
        risk_free_rate = st.slider(
            "Risk-Free Rate",
            min_value=0.0,
            max_value=0.1,
            value=0.02,
            step=0.005,
            format="%.3f"
        )
        
        enable_ml = st.checkbox(
            "Enable ML Prediction",
            value=True,
            help="Use machine learning for return prediction"
        )
        
        min_weight, max_weight = st.slider(
            "Weight Bounds",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.05,
            help="Minimum and maximum weight for any single asset"
        )
        
        # Date range
        st.subheader("Data Range")
        use_default_dates = st.checkbox("Use default 5-year period", value=True)
        
        if not use_default_dates:
            end_date = st.date_input("End Date", datetime.now().date())
            start_date = st.date_input(
                "Start Date", 
                end_date - timedelta(days=365*5)
            )
        else:
            start_date = None
            end_date = None
        
        # Optimization button
        optimize_button = st.button(
            "🚀 Optimize Portfolio",
            type="primary",
            disabled=len(tickers) < 2
        )
    
    # Main content area
    if optimize_button and len(tickers) >= 2:
        run_optimization(
            tickers=tickers,
            optimization_method=optimization_method,
            risk_free_rate=risk_free_rate,
            enable_ml=enable_ml,
            weight_bounds=(min_weight, max_weight),
            start_date=start_date,
            end_date=end_date
        )
    else:
        show_welcome_screen()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Portfolio Optimization AI Dashboard | Powered by Modern Portfolio Theory & Machine Learning"
        "</div>",
        unsafe_allow_html=True
    )

def get_manual_tickers():
    """Get tickers from manual input."""
    tickers_input = st.text_area(
        "Enter Stock Tickers",
        placeholder="AAPL, MSFT, GOOG, AMZN\n\nEnter one ticker per line or comma-separated",
        help="Enter stock symbols (e.g., AAPL, MSFT, GOOG)"
    )
    
    tickers = []
    if tickers_input:
        # Parse tickers
        tickers = [ticker.strip().upper() for ticker in tickers_input.replace('\n', ',').split(',')]
        tickers = [ticker for ticker in tickers if ticker]  # Remove empty strings
    
    return tickers

def get_predefined_portfolios():
    """Get tickers from predefined portfolios."""
    portfolio_options = {
        "Tech Giants": ["AAPL", "MSFT", "GOOG", "AMZN", "META"],
        "S&P 500 Top 10": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "JNJ", "V"],
        "Diversified Growth": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "ADBE", "CRM"],
        "Blue Chip": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "JPM", "JNJ", "V", "PG", "KO"],
        "Custom Mix": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    }
    
    portfolio_name = st.selectbox("Select Portfolio", list(portfolio_options.keys()))
    tickers = portfolio_options[portfolio_name]
    
    # Display selected tickers
    st.write("Selected tickers:")
    for ticker in tickers:
        st.write(f"• {ticker}")
    
    return tickers

def run_optimization(tickers, optimization_method, risk_free_rate, enable_ml, weight_bounds, start_date, end_date):
    """Run portfolio optimization."""
    
    # Show loading
    with st.spinner("Optimizing portfolio... This may take a few minutes."):
        try:
            # Prepare request
            request_data = {
                "tickers": tickers,
                "optimization_method": optimization_method,
                "risk_free_rate": risk_free_rate,
                "enable_ml_prediction": enable_ml,
                "weight_bounds": weight_bounds
            }
            
            if start_date and end_date:
                request_data["start_date"] = start_date.strftime("%Y-%m-%d")
                request_data["end_date"] = end_date.strftime("%Y-%m-%d")
            
            # Call API
            response = requests.post(
                f"{API_BASE_URL}/optimize/sync",
                json=request_data,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                results = response.json()
                display_optimization_results(results, tickers)
            else:
                error_msg = response.json().get("detail", "Unknown error")
                st.error(f"Optimization failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            st.error("Optimization timed out. Please try again with fewer tickers or use the async endpoint.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API server. Please ensure the server is running on localhost:8000")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def display_optimization_results(results, tickers):
    """Display optimization results."""
    
    if not results.get("success"):
        st.error("Optimization failed")
        return
    
    data = results.get("data", {})
    
    # Success message
    st.markdown(
        '<div class="success-message">✅ Portfolio optimization completed successfully!</div>',
        unsafe_allow_html=True
    )
    
    # Key metrics
    st.header("📈 Portfolio Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Expected Return",
            f"{data['portfolio']['expected_return']:.2%}",
            help="Annualized expected return"
        )
    
    with col2:
        st.metric(
            "Volatility",
            f"{data['portfolio']['volatility']:.2%}",
            help="Annualized volatility"
        )
    
    with col3:
        st.metric(
            "Sharpe Ratio",
            f"{data['portfolio']['sharpe_ratio']:.3f}",
            help="Risk-adjusted return measure"
        )
    
    with col4:
        st.metric(
            "Assets",
            len(data['portfolio']['weights']),
            help="Number of assets in portfolio"
        )
    
    # Portfolio allocation
    st.header("🎯 Portfolio Allocation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        weights_df = pd.DataFrame(list(data['portfolio']['weights'].items()), columns=['Ticker', 'Weight'])
        weights_df = weights_df.sort_values('Weight', ascending=False)
        
        fig_pie = px.pie(
            weights_df,
            values='Weight',
            names='Ticker',
            title='Portfolio Allocation'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart
        fig_bar = px.bar(
            weights_df,
            x='Ticker',
            y='Weight',
            title='Asset Weights',
            labels={'Weight': 'Portfolio Weight'}
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Weight details table
    st.subheader("Weight Details")
    weights_df['Weight (%)'] = weights_df['Weight'] * 100
    weights_df['Expected Return (%)'] = [data.get('expected_returns', {}).get(ticker, 0) * 100 for ticker in weights_df['Ticker']]
    
    st.dataframe(
        weights_df[['Ticker', 'Weight (%)', 'Expected Return (%)']],
        use_container_width=True
    )
    
    # Risk metrics
    if data.get('risk_metrics'):
        st.header("⚠️ Risk Analysis")
        
        risk_metrics = data['risk_metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if risk_metrics.get('sortino_ratio'):
                st.metric("Sortino Ratio", f"{risk_metrics['sortino_ratio']:.3f}")
        
        with col2:
            if risk_metrics.get('max_drawdown'):
                st.metric("Max Drawdown", f"{risk_metrics['max_drawdown']:.2%}")
        
        with col3:
            if risk_metrics.get('var_95%'):
                st.metric("VaR (95%)", f"{risk_metrics['var_95%']:.2%}")
        
        with col4:
            if risk_metrics.get('calmar_ratio'):
                st.metric("Calmar Ratio", f"{risk_metrics['calmar_ratio']:.3f}")
    
    # Insights
    if data.get('insights'):
        st.header("💡 Portfolio Insights")
        
        insights = data['insights']
        
        if insights.get('concentration'):
            concentration = insights['concentration']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Concentration (HHI)",
                    f"{concentration.get('herfindahl_index', 0):.3f}",
                    help="Herfindahl-Hirschman Index (lower = more diversified)"
                )
            
            with col2:
                st.metric(
                    "Max Weight",
                    f"{concentration.get('max_weight', 0):.2%}"
                )
            
            with col3:
                st.metric(
                    "Weight Std Dev",
                    f"{concentration.get('weight_std', 0):.3f}"
                )
    
    # Data summary
    if data.get('data_summary'):
        st.header("📊 Data Summary")
        
        summary = data['data_summary']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Data Points", summary.get('data_points', 'N/A'))
        
        with col2:
            if summary.get('date_range'):
                date_range = summary['date_range']
                st.metric(
                    "Date Range",
                    f"{date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}"
                )
    
    # Export results
    st.header("📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download as JSON
        results_json = json.dumps(results, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=results_json,
            file_name=f"portfolio_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Download weights as CSV
        weights_df.to_csv(
            f"portfolio_weights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            index=False
        )
        st.download_button(
            label="📊 Download CSV",
            data=weights_df.to_csv(index=False),
            file_name=f"portfolio_weights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_welcome_screen():
    """Show welcome screen when no optimization has been run."""
    
    st.markdown("## Welcome to Portfolio Optimization AI!")
    
    st.markdown("""
    ### 🚀 Features
    
    - **AI-Powered Return Prediction**: Uses machine learning models (Random Forest, XGBoost) to predict expected returns
    - **Modern Portfolio Theory**: Implements Markowitz's mean-variance optimization
    - **Multiple Optimization Strategies**: Max Sharpe ratio, minimum volatility, equal weight
    - **Comprehensive Risk Analysis**: VaR, drawdown, Sortino ratio, and more
    - **Interactive Visualizations**: Portfolio allocation charts and risk metrics
    
    ### 📋 How to Use
    
    1. **Select Tickers**: Choose stocks either manually or from predefined portfolios
    2. **Configure Parameters**: Set optimization method, risk-free rate, and constraints
    3. **Run Optimization**: Click the optimize button to generate optimal portfolio weights
    4. **Analyze Results**: Review portfolio metrics, risk analysis, and insights
    
    ### 🎯 Optimization Methods
    
    - **Maximum Sharpe Ratio**: Maximizes risk-adjusted returns
    - **Minimum Volatility**: Minimizes portfolio risk
    - **Equal Weight**: Simple equal allocation across all assets
    
    ### ⚙️ Technical Details
    
    - **Data Source**: Yahoo Finance (yfinance)
    - **ML Models**: RandomForestRegressor, XGBoostRegressor
    - **Features**: Technical indicators (RSI, MACD, Bollinger Bands, momentum, etc.)
    - **Optimization**: scipy.optimize with constraints
    - **Risk Metrics**: VaR, maximum drawdown, Sortino ratio, Calmar ratio
    """)
    
    # Example portfolio
    st.markdown("### 📊 Example Portfolio")
    
    example_tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
    
    if st.button("🎯 Try Example Portfolio"):
        st.session_state.example_tickers = example_tickers
        st.rerun()
    
    # Display example if selected
    if 'example_tickers' in st.session_state:
        st.info(f"Example tickers loaded: {', '.join(st.session_state.example_tickers)}")
        st.info("Configure parameters in the sidebar and click 'Optimize Portfolio' to see results!")

def check_api_connection():
    """Check if API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    # Check API connection
    if not check_api_connection():
        st.warning("⚠️ API server is not running. Start the server with: `uvicorn api.server:app --reload`")
    
    main()
