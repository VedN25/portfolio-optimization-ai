#!/usr/bin/env python3
"""
Simple standalone dashboard for Portfolio Optimization AI
"""

import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Page config
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
</style>
""", unsafe_allow_html=True)

def run_portfolio_optimization(tickers, method="max_sharpe"):
    """Run portfolio optimization using the pipeline"""
    try:
        from pipeline import PortfolioOptimizationPipeline
        
        # Initialize pipeline
        pipeline = PortfolioOptimizationPipeline()
        
        # Run optimization
        results = pipeline.run(tickers)
        
        return results, None
        
    except Exception as e:
        return None, str(e)

def main():
    """Main dashboard function"""
    
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
            tickers_input = st.text_area(
                "Enter Stock Tickers",
                placeholder="AAPL, MSFT, GOOG, AMZN\n\nEnter one ticker per line or comma-separated",
                help="Enter stock symbols (e.g., AAPL, MSFT, GOOG)"
            )
            
            if tickers_input:
                tickers = [ticker.strip().upper() for ticker in tickers_input.replace('\n', ',').split(',')]
                tickers = [ticker for ticker in tickers if ticker]
            else:
                tickers = []
        else:
            portfolio_options = {
                "Tech Giants": ["AAPL", "MSFT", "GOOG", "AMZN", "META"],
                "S&P 500 Top 10": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", "JNJ", "V"],
                "Diversified Growth": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "ADBE", "CRM"],
                "Blue Chip": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "JPM", "JNJ", "V", "PG", "KO"]
            }
            
            portfolio_name = st.selectbox("Select Portfolio", list(portfolio_options.keys()))
            tickers = portfolio_options[portfolio_name]
            
            st.write("Selected tickers:")
            for ticker in tickers:
                st.write(f"• {ticker}")
        
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
        
        # Optimization button
        optimize_button = st.button(
            "🚀 Optimize Portfolio",
            type="primary",
            disabled=len(tickers) < 2
        )
    
    # Main content area
    if optimize_button and len(tickers) >= 2:
        with st.spinner("Optimizing portfolio... This may take a few minutes."):
            results, error = run_portfolio_optimization(tickers, optimization_method)
            
            if results:
                display_optimization_results(results, tickers)
            else:
                st.error(f"Optimization failed: {error}")
                st.info("💡 This might be due to network issues or missing dependencies. Try installing: pip install -r requirements.txt")
    else:
        show_welcome_screen()

def display_optimization_results(results, tickers):
    """Display optimization results"""
    
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
            f"{results['optimization_result']['expected_return']:.2%}",
            help="Annualized expected return"
        )
    
    with col2:
        st.metric(
            "Volatility",
            f"{results['optimization_result']['volatility']:.2%}",
            help="Annualized volatility"
        )
    
    with col3:
        st.metric(
            "Sharpe Ratio",
            f"{results['optimization_result']['sharpe_ratio']:.3f}",
            help="Risk-adjusted return measure"
        )
    
    with col4:
        st.metric(
            "Assets",
            len(results['optimization_result']['weights']),
            help="Number of assets in portfolio"
        )
    
    # Portfolio allocation
    st.header("🎯 Portfolio Allocation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        weights_df = pd.DataFrame(list(results['optimization_result']['weights'].items()), columns=['Ticker', 'Weight'])
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
    weights_df['Expected Return (%)'] = [results.get('expected_returns', {}).get(ticker, 0) * 100 for ticker in weights_df['Ticker']]
    
    st.dataframe(
        weights_df[['Ticker', 'Weight (%)', 'Expected Return (%)']],
        use_container_width=True
    )
    
    # Risk metrics
    if results.get('risk_metrics'):
        st.header("⚠️ Risk Analysis")
        
        risk_metrics = results['risk_metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if risk_metrics.get('sortino_ratio'):
                st.metric("Sortino Ratio", f"{risk_metrics['sortino_ratio']:.3f}")
        
        with col2:
            if risk_metrics.get('max_drawdown'):
                st.metric("Max Drawdown", f"{risk_metrics['drawdown_analysis']['max_drawdown']:.2%}")
        
        with col3:
            if risk_metrics.get('var_95%'):
                st.metric("VaR (95%)", f"{risk_metrics['var_95%']['var_5%']:.2%}")
        
        with col4:
            if risk_metrics.get('calmar_ratio'):
                st.metric("Calmar Ratio", f"{risk_metrics['calmar_ratio']:.3f}")
    
    # Export results
    st.header("📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download as JSON
        import json
        results_json = json.dumps(results, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=results_json,
            file_name=f"portfolio_optimization_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Download weights as CSV
        st.download_button(
            label="📊 Download CSV",
            data=weights_df.to_csv(index=False),
            file_name=f"portfolio_weights_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_welcome_screen():
    """Show welcome screen when no optimization has been run"""
    
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
    
    if st.button("🎯 Try Example Portfolio"):
        st.session_state.example_tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
        st.info(f"Example tickers loaded: {', '.join(st.session_state.example_tickers)}")
        st.info("Configure parameters in the sidebar and click 'Optimize Portfolio' to see results!")

if __name__ == "__main__":
    main()
