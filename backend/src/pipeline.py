"""
Portfolio Optimization Pipeline

This module creates the end-to-end workflow for portfolio optimization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from return_predictor import ReturnPredictor, ModelConfig
from portfolio_optimizer import PortfolioOptimizer, OptimizationResult
from risk_metrics import RiskMetrics

logger = logging.getLogger(__name__)


class PortfolioOptimizationPipeline:
    """
    End-to-end pipeline for portfolio optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the pipeline.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        
        # Initialize components
        self.data_loader = DataLoader()
        self.feature_engineer = FeatureEngineer()
        self.return_predictor = ReturnPredictor(
            config=ModelConfig(**self.config.get('model_config', {}))
        )
        self.portfolio_optimizer = PortfolioOptimizer(
            risk_free_rate=self.config.get('risk_free_rate', 0.02)
        )
        self.risk_metrics = RiskMetrics(
            risk_free_rate=self.config.get('risk_free_rate', 0.02)
        )
        
        # Storage for intermediate results
        self.price_data = None
        self.features_dict = {}
        self.expected_returns = {}
        self.optimization_result = None
        self.risk_analysis = None
        
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'risk_free_rate': 0.02,
            'data_period': '5y',
            'model_config': {
                'random_state': 42,
                'test_size': 0.2,
                'rf_n_estimators': 100,
                'xgb_n_estimators': 100
            },
            'optimization_method': 'max_sharpe',
            'weight_bounds': (0.0, 1.0),
            'enable_ml_prediction': True
        }
    
    def run(
        self, 
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete portfolio optimization pipeline.
        
        Args:
            tickers: List of stock tickers
            start_date: Start date for data (optional)
            end_date: End date for data (optional)
        
        Returns:
            Dictionary with complete results
        """
        logger.info(f"Starting portfolio optimization pipeline for {len(tickers)} tickers")
        
        try:
            # Step 1: Download data
            self.price_data = self._download_data(tickers, start_date, end_date)
            
            # Step 2: Generate features
            self.features_dict = self._generate_features()
            
            # Step 3: Predict expected returns
            self.expected_returns = self._predict_expected_returns()
            
            # Step 4: Calculate covariance matrix
            covariance_matrix = self._calculate_covariance_matrix()
            
            # Step 5: Optimize portfolio
            self.optimization_result = self._optimize_portfolio(covariance_matrix)
            
            # Step 6: Calculate risk metrics
            self.risk_analysis = self._calculate_risk_metrics()
            
            # Step 7: Generate additional insights
            insights = self._generate_insights()
            
            # Compile results
            results = self._compile_results(insights)
            
            logger.info("Pipeline completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise
    
    def _download_data(
        self, 
        tickers: List[str], 
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """
        Download stock price data.
        
        Args:
            tickers: List of stock tickers
            start_date: Start date
            end_date: End date
        
        Returns:
            DataFrame with price data
        """
        logger.info("Downloading stock price data...")
        
        if start_date and end_date:
            data = self.data_loader.download_stock_data(tickers, start_date, end_date)
        else:
            data = self.data_loader.download_stock_data(
                tickers, 
                period=self.config.get('data_period', '5y')
            )
        
        # Validate data quality
        quality_report = self.data_loader.validate_data_quality()
        if quality_report['data_quality'] == 'poor':
            logger.warning("Data quality issues detected")
        
        logger.info(f"Downloaded data for {len(data.columns)} tickers")
        return data
    
    def _generate_features(self) -> Dict[str, pd.DataFrame]:
        """
        Generate features for each ticker.
        
        Returns:
            Dictionary of features by ticker
        """
        logger.info("Generating features...")
        
        # Create feature matrix
        all_features = self.feature_engineer.create_feature_matrix(self.price_data)
        
        # Split features by ticker for individual prediction
        features_dict = {}
        
        for ticker in self.price_data.columns:
            # Get features for this ticker (exclude other tickers' data)
            ticker_features = {}
            
            for col in all_features.columns:
                if ticker in col:
                    ticker_features[col] = all_features[col]
            
            if ticker_features:
                features_dict[ticker] = pd.DataFrame(ticker_features)
        
        logger.info(f"Generated features for {len(features_dict)} tickers")
        return features_dict
    
    def _predict_expected_returns(self) -> Dict[str, float]:
        """
        Predict expected returns using ML models.
        
        Returns:
            Dictionary of expected returns by ticker
        """
        logger.info("Predicting expected returns...")
        
        expected_returns = {}
        
        if self.config.get('enable_ml_prediction', True):
            # Use ML models for prediction
            for ticker, features in self.features_dict.items():
                try:
                    # Get features and target
                    X, y = self.feature_engineer.get_feature_importance_data(ticker)
                    
                    if len(X) < 100:  # Need minimum data for training
                        logger.warning(f"Insufficient data for {ticker}, using historical mean")
                        returns = self.data_loader.get_returns()
                        expected_returns[ticker] = returns[ticker].mean() * 252
                        continue
                    
                    # Train models
                    rf_results = self.return_predictor.train_random_forest(X, y, f"rf_{ticker}")
                    xgb_results = self.return_predictor.train_xgboost(X, y, f"xgb_{ticker}")
                    
                    # Get best model
                    best_model_name, _ = self.return_predictor.get_best_model()
                    
                    # Predict expected return (use most recent features)
                    latest_features = features.iloc[-1:].copy()
                    predicted_return = self.return_predictor.predict_returns(
                        latest_features, best_model_name
                    )
                    
                    # Annualize the return
                    expected_returns[ticker] = float(predicted_return[0]) * 252
                    
                except Exception as e:
                    logger.warning(f"ML prediction failed for {ticker}: {str(e)}")
                    # Fallback to historical mean
                    returns = self.data_loader.get_returns()
                    expected_returns[ticker] = returns[ticker].mean() * 252
        else:
            # Use historical returns
            returns = self.data_loader.get_returns()
            for ticker in self.price_data.columns:
                expected_returns[ticker] = returns[ticker].mean() * 252
        
        logger.info(f"Predicted returns for {len(expected_returns)} tickers")
        return expected_returns
    
    def _calculate_covariance_matrix(self) -> pd.DataFrame:
        """
        Calculate covariance matrix of returns.
        
        Returns:
            Covariance matrix
        """
        logger.info("Calculating covariance matrix...")
        
        # Get returns
        returns = self.data_loader.get_returns()
        
        # Calculate annualized covariance matrix
        cov_matrix = returns.cov() * 252
        
        return cov_matrix
    
    def _optimize_portfolio(self, covariance_matrix: pd.DataFrame) -> OptimizationResult:
        """
        Optimize portfolio weights.
        
        Args:
            covariance_matrix: Covariance matrix
        
        Returns:
            Optimization result
        """
        logger.info("Optimizing portfolio...")
        
        # Set optimizer inputs
        self.portfolio_optimizer.set_inputs(self.expected_returns, covariance_matrix)
        
        # Choose optimization method
        method = self.config.get('optimization_method', 'max_sharpe')
        weight_bounds = self.config.get('weight_bounds', (0.0, 1.0))
        
        if method == 'max_sharpe':
            result = self.portfolio_optimizer.optimize_max_sharpe(weight_bounds)
        elif method == 'min_volatility':
            result = self.portfolio_optimizer.optimize_min_volatility(weight_bounds)
        elif method == 'equal_weight':
            result = self.portfolio_optimizer.optimize_equal_weight()
        else:
            raise ValueError(f"Unknown optimization method: {method}")
        
        if not result.success:
            logger.warning(f"Optimization failed: {result.message}")
            # Fallback to equal weights
            result = self.portfolio_optimizer.optimize_equal_weight()
        
        logger.info(f"Portfolio optimization completed. Sharpe ratio: {result.sharpe_ratio:.4f}")
        return result
    
    def _calculate_risk_metrics(self) -> Dict[str, Any]:
        """
        Calculate risk metrics for the optimized portfolio.
        
        Returns:
            Risk analysis results
        """
        logger.info("Calculating risk metrics...")
        
        # Calculate portfolio returns
        returns = self.data_loader.get_returns()
        portfolio_returns = pd.Series(0.0, index=returns.index)
        
        for ticker, weight in self.optimization_result.weights.items():
            if ticker in returns.columns:
                portfolio_returns += returns[ticker] * weight
        
        # Calculate portfolio values
        portfolio_values = (1 + portfolio_returns).cumprod()
        
        # Comprehensive risk analysis
        risk_analysis = self.risk_metrics.comprehensive_risk_analysis(
            portfolio_returns, portfolio_values
        )
        
        return risk_analysis
    
    def _generate_insights(self) -> Dict[str, Any]:
        """
        Generate additional insights and analysis.
        
        Returns:
            Dictionary with insights
        """
        logger.info("Generating insights...")
        
        insights = {}
        
        # Efficient frontier
        try:
            efficient_frontier = self.portfolio_optimizer.generate_efficient_frontier(num_portfolios=50)
            insights['efficient_frontier'] = efficient_frontier.to_dict('records')
        except Exception as e:
            logger.warning(f"Failed to generate efficient frontier: {str(e)}")
        
        # Monte Carlo simulation
        try:
            monte_carlo = self.portfolio_optimizer.monte_carlo_simulation(num_portfolios=1000)
            insights['monte_carlo_simulation'] = {
                'num_portfolios': len(monte_carlo),
                'max_sharpe': monte_carlo['sharpe_ratio'].max(),
                'min_volatility': monte_carlo['volatility'].min(),
                'max_return': monte_carlo['return'].max()
            }
        except Exception as e:
            logger.warning(f"Failed to run Monte Carlo simulation: {str(e)}")
        
        # Portfolio concentration
        weights = list(self.optimization_result.weights.values())
        herfindahl_index = sum(w**2 for w in weights)
        insights['concentration_metrics'] = {
            'herfindahl_index': herfindahl_index,
            'max_weight': max(weights),
            'min_weight': min(weights),
            'weight_std': np.std(weights)
        }
        
        return insights
    
    def _compile_results(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile all results into a comprehensive dictionary.
        
        Args:
            insights: Additional insights
        
        Returns:
            Complete results dictionary
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'tickers': self.price_data.columns.tolist(),
            'optimization_result': {
                'weights': self.optimization_result.weights,
                'expected_return': self.optimization_result.expected_return,
                'volatility': self.optimization_result.volatility,
                'sharpe_ratio': self.optimization_result.sharpe_ratio,
                'success': self.optimization_result.success,
                'message': self.optimization_result.message
            },
            'expected_returns': self.expected_returns,
            'risk_metrics': self.risk_analysis,
            'insights': insights,
            'data_summary': {
                'data_points': len(self.price_data),
                'date_range': {
                    'start': self.price_data.index[0].strftime('%Y-%m-%d'),
                    'end': self.price_data.index[-1].strftime('%Y-%m-%d')
                }
            }
        }
        
        return results
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get a concise summary of the portfolio optimization results.
        
        Returns:
            Portfolio summary
        """
        if self.optimization_result is None:
            return {"status": "No optimization performed"}
        
        summary = {
            'optimization_method': self.config.get('optimization_method', 'max_sharpe'),
            'expected_annual_return': self.optimization_result.expected_return,
            'annual_volatility': self.optimization_result.volatility,
            'sharpe_ratio': self.optimization_result.sharpe_ratio,
            'num_assets': len(self.optimization_result.weights),
            'top_holdings': sorted(
                self.optimization_result.weights.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
        
        if self.risk_analysis:
            summary['risk_metrics'] = {
                'max_drawdown': self.risk_analysis['drawdown_analysis']['max_drawdown'],
                'var_95%': self.risk_analysis['var_95%']['var_5%'],
                'sortino_ratio': self.risk_analysis['sortino_ratio'],
                'calmar_ratio': self.risk_analysis['calmar_ratio']
            }
        
        return summary


if __name__ == "__main__":
    # Example usage
    pipeline = PortfolioOptimizationPipeline()
    
    # Run optimization
    tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
    results = pipeline.run(tickers)
    
    print("Portfolio Optimization Results:")
    print(f"Expected Return: {results['optimization_result']['expected_return']:.4f}")
    print(f"Volatility: {results['optimization_result']['volatility']:.4f}")
    print(f"Sharpe Ratio: {results['optimization_result']['sharpe_ratio']:.4f}")
    print("\nOptimal Weights:")
    for ticker, weight in results['optimization_result']['weights'].items():
        print(f"  {ticker}: {weight:.4f}")
    
    # Get summary
    summary = pipeline.get_portfolio_summary()
    print("\nPortfolio Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
