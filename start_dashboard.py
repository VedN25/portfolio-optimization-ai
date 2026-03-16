#!/usr/bin/env python3
"""
Simple dashboard launcher for Portfolio Optimization AI
"""

import streamlit as st
import sys
import os

def main():
    """Launch the dashboard"""
    # Add src to path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    # Page config
    st.set_page_config(
        page_title="Portfolio Optimization AI",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.markdown('<h1 class="main-header">📊 Portfolio Optimization AI</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Welcome message
    st.markdown("""
    ## 🚀 Welcome to Portfolio Optimization AI!
    
    ### 📋 Quick Start
    
    1. **Enter Tickers**: Add stock symbols (e.g., AAPL, MSFT, GOOG, AMZN)
    2. **Configure Settings**: Choose optimization method and parameters
    3. **Run Optimization**: Click the optimize button
    4. **View Results**: Analyze portfolio allocation and risk metrics
    
    ### 🎯 Example Portfolios
    
    - **Tech Giants**: AAPL, MSFT, GOOG, AMZN, META
    - **S&P 500**: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA
    - **Blue Chip**: AAPL, MSFT, JPM, JNJ, V, PG
    
    ### 📊 Features
    
    - 🤖 AI-powered return prediction
    - 📈 Modern Portfolio Theory optimization
    - ⚠️ Comprehensive risk analysis
    - 📱 Mobile-friendly interface
    
    ---
    
    **📝 Note**: This is the simplified dashboard. For the full experience, ensure the API server is running on port 8000.
    """)
    
    # Demo section
    st.markdown("### 🎮 Try Demo")
    
    if st.button("🚀 Run Demo Optimization"):
        with st.spinner("Running portfolio optimization..."):
            try:
                from pipeline import PortfolioOptimizationPipeline
                
                # Run demo
                pipeline = PortfolioOptimizationPipeline()
                tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
                results = pipeline.run(tickers)
                
                # Display results
                st.success("✅ Optimization Complete!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Expected Return",
                        f"{results['optimization_result']['expected_return']:.2%}"
                    )
                
                with col2:
                    st.metric(
                        "Volatility",
                        f"{results['optimization_result']['volatility']:.2%}"
                    )
                
                with col3:
                    st.metric(
                        "Sharpe Ratio",
                        f"{results['optimization_result']['sharpe_ratio']:.3f}"
                    )
                
                # Portfolio allocation
                st.subheader("🎯 Portfolio Allocation")
                weights = results['optimization_result']['weights']
                
                import plotly.express as px
                import pandas as pd
                
                weights_df = pd.DataFrame(list(weights.items()), columns=['Ticker', 'Weight'])
                
                fig = px.pie(
                    weights_df,
                    values='Weight',
                    names='Ticker',
                    title='Portfolio Allocation'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure you have the required dependencies installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
