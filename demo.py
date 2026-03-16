#!/usr/bin/env python3
"""
Portfolio Optimization AI Demo

This script demonstrates the complete portfolio optimization system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run the portfolio optimization demo."""
    print("🚀 Portfolio Optimization AI Demo")
    print("=" * 50)
    
    # Import the pipeline
    try:
        from pipeline import PortfolioOptimizationPipeline
        print("✅ Successfully imported portfolio optimization modules")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return
    
    # Initialize pipeline
    print("\n🔧 Initializing portfolio optimization pipeline...")
    pipeline = PortfolioOptimizationPipeline()
    
    # Define demo tickers
    tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
    print(f"📊 Optimizing portfolio for: {', '.join(tickers)}")
    
    try:
        print("\n🔄 Running optimization pipeline...")
        print("   1. Downloading historical data...")
        print("   2. Engineering features...")
        print("   3. Training ML models...")
        print("   4. Optimizing portfolio...")
        print("   5. Calculating risk metrics...")
        
        # Run the complete pipeline
        results = pipeline.run(tickers)
        
        print("\n✅ Optimization Complete!")
        print("\n" + "=" * 50)
        print("📈 PORTFOLIO RESULTS")
        print("=" * 50)
        
        # Display portfolio metrics
        portfolio = results["optimization_result"]
        print(f"Expected Annual Return: {portfolio['expected_return']:.2%}")
        print(f"Annual Volatility:     {portfolio['volatility']:.2%}")
        print(f"Sharpe Ratio:          {portfolio['sharpe_ratio']:.3f}")
        
        print("\n🎯 OPTIMAL ALLOCATION")
        print("-" * 30)
        weights = portfolio["weights"]
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        for ticker, weight in sorted_weights:
            print(f"{ticker:<6} {weight:>6.2%}")
        
        print(f"\n{'Total':<6} {sum(weights.values()):>6.2%}")
        
        # Display risk metrics if available
        if "risk_metrics" in results:
            risk = results["risk_metrics"]
            print("\n⚠️  RISK ANALYSIS")
            print("-" * 30)
            print(f"Sortino Ratio:     {risk.get('sortino_ratio', 0):.3f}")
            print(f"Max Drawdown:      {risk.get('drawdown_analysis', {}).get('max_drawdown', 0):.2%}")
            print(f"VaR (95%):         {risk.get('var_95%', {}).get('var_5%', 0):.2%}")
            print(f"Calmar Ratio:      {risk.get('calmar_ratio', 0):.3f}")
        
        # Display insights
        if "insights" in results:
            insights = results["insights"]
            if "concentration" in insights:
                conc = insights["concentration"]
                print("\n💡 PORTFOLIO INSIGHTS")
                print("-" * 30)
                print(f"Concentration (HHI): {conc.get('herfindahl_index', 0):.3f}")
                print(f"Max Weight:          {conc.get('max_weight', 0):.2%}")
                print(f"Diversification:     {'High' if conc.get('herfindahl_index', 0) < 0.3 else 'Medium' if conc.get('herfindahl_index', 0) < 0.5 else 'Low'}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n" + "=" * 50)
        print("📚 NEXT STEPS")
        print("=" * 50)
        print("1. Start API server: uvicorn api.server:app --reload")
        print("2. Launch dashboard: streamlit run dashboard/app.py")
        print("3. Visit API docs: http://localhost:8000/docs")
        print("4. Try different tickers and optimization methods!")
        
    except Exception as e:
        print(f"\n❌ Error during optimization: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check internet connection")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Try with fewer tickers")
        print("4. Check if yfinance can access market data")

if __name__ == "__main__":
    main()
