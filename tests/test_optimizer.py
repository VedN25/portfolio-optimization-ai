"""
Test Suite for Portfolio Optimizer

This module contains unit tests for the portfolio optimization components.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from portfolio_optimizer import PortfolioOptimizer, OptimizationResult
from risk_metrics import RiskMetrics
from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from return_predictor import ReturnPredictor


class TestPortfolioOptimizer:
    """Test cases for PortfolioOptimizer class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
        
        # Sample expected returns (annualized)
        expected_returns = {
            "AAPL": 0.15,
            "MSFT": 0.12,
            "GOOG": 0.10,
            "AMZN": 0.18
        }
        
        # Sample covariance matrix
        cov_matrix = pd.DataFrame(
            [[0.04, 0.02, 0.01, 0.03],
             [0.02, 0.03, 0.01, 0.02],
             [0.01, 0.01, 0.02, 0.01],
             [0.03, 0.02, 0.01, 0.05]],
            index=tickers,
            columns=tickers
        )
        
        return expected_returns, cov_matrix
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return PortfolioOptimizer(risk_free_rate=0.02)
    
    def test_initialization(self, optimizer):
        """Test optimizer initialization."""
        assert optimizer.risk_free_rate == 0.02
        assert optimizer.expected_returns is None
        assert optimizer.covariance_matrix is None
        assert optimizer.tickers is None
    
    def test_set_inputs(self, optimizer, sample_data):
        """Test setting optimizer inputs."""
        expected_returns, cov_matrix = sample_data
        
        optimizer.set_inputs(expected_returns, cov_matrix)
        
        assert optimizer.expected_returns == expected_returns
        assert optimizer.covariance_matrix.equals(cov_matrix)
        assert optimizer.tickers == list(expected_returns.keys())
    
    def test_set_inputs_validation(self, optimizer, sample_data):
        """Test input validation."""
        expected_returns, cov_matrix = sample_data
        
        # Mismatched dimensions
        wrong_returns = {"AAPL": 0.15, "MSFT": 0.12}
        
        with pytest.raises(ValueError):
            optimizer.set_inputs(wrong_returns, cov_matrix)
        
        # Mismatched tickers
        wrong_cov = cov_matrix.copy()
        wrong_cov.columns = ["AAPL", "MSFT", "GOOG", "TSLA"]
        
        with pytest.raises(ValueError):
            optimizer.set_inputs(expected_returns, wrong_cov)
    
    def test_calculate_portfolio_metrics(self, optimizer, sample_data):
        """Test portfolio metrics calculation."""
        expected_returns, cov_matrix = sample_data
        optimizer.set_inputs(expected_returns, cov_matrix)
        
        weights = np.array([0.25, 0.25, 0.25, 0.25])
        portfolio_return, volatility, sharpe_ratio = optimizer.calculate_portfolio_metrics(weights)
        
        assert isinstance(portfolio_return, float)
        assert isinstance(volatility, float)
        assert isinstance(sharpe_ratio, float)
        assert volatility > 0
        assert sharpe_ratio > 0
    
    def test_optimize_max_sharpe(self, optimizer, sample_data):
        """Test maximum Sharpe ratio optimization."""
        expected_returns, cov_matrix = sample_data
        optimizer.set_inputs(expected_returns, cov_matrix)
        
        result = optimizer.optimize_max_sharpe()
        
        assert isinstance(result, OptimizationResult)
        assert result.success
        assert len(result.weights) == 4
        assert sum(result.weights.values()) == pytest.approx(1.0, rel=1e-3)
        assert all(w >= 0 for w in result.weights.values())
        assert result.expected_return > 0
        assert result.volatility > 0
        assert result.sharpe_ratio > 0
    
    def test_optimize_min_volatility(self, optimizer, sample_data):
        """Test minimum volatility optimization."""
        expected_returns, cov_matrix = sample_data
        optimizer.set_inputs(expected_returns, cov_matrix)
        
        result = optimizer.optimize_min_volatility()
        
        assert isinstance(result, OptimizationResult)
        assert result.success
        assert len(result.weights) == 4
        assert sum(result.weights.values()) == pytest.approx(1.0, rel=1e-3)
        assert all(w >= 0 for w in result.weights.values())
    
    def test_optimize_equal_weight(self, optimizer, sample_data):
        """Test equal weight portfolio."""
        expected_returns, cov_matrix = sample_data
        optimizer.set_inputs(expected_returns, cov_matrix)
        
        result = optimizer.optimize_equal_weight()
        
        assert isinstance(result, OptimizationResult)
        assert result.success
        assert len(result.weights) == 4
        assert all(w == pytest.approx(0.25, rel=1e-3) for w in result.weights.values())
    
    def test_monte_carlo_simulation(self, optimizer, sample_data):
        """Test Monte Carlo simulation."""
        expected_returns, cov_matrix = sample_data
        optimizer.set_inputs(expected_returns, cov_matrix)
        
        results = optimizer.monte_carlo_simulation(num_portfolios=100)
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 100
        assert 'return' in results.columns
        assert 'volatility' in results.columns
        assert 'sharpe_ratio' in results.columns
        assert 'weights' in results.columns
    
    def test_generate_efficient_frontier(self, optimizer, sample_data):
        """Test efficient frontier generation."""
        expected_returns, cov_matrix = sample_data
        optimizer.set_inputs(expected_returns, cov_matrix)
        
        efficient_frontier = optimizer.generate_efficient_frontier(num_portfolios=20)
        
        assert isinstance(efficient_frontier, pd.DataFrame)
        assert len(efficient_frontier) <= 20
        assert 'return' in efficient_frontier.columns
        assert 'volatility' in efficient_frontier.columns
        assert 'sharpe_ratio' in efficient_frontier.columns


class TestRiskMetrics:
    """Test cases for RiskMetrics class."""
    
    @pytest.fixture
    def risk_calculator(self):
        """Create risk metrics calculator."""
        return RiskMetrics(risk_free_rate=0.02)
    
    @pytest.fixture
    def sample_returns(self):
        """Create sample returns data."""
        np.random.seed(42)
        dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='D')
        returns = pd.Series(
            np.random.normal(0.0005, 0.02, len(dates)),
            index=dates
        )
        return returns
    
    @pytest.fixture
    def sample_prices(self, sample_returns):
        """Create sample price data."""
        prices = pd.Series(
            100 * (1 + sample_returns).cumprod(),
            index=sample_returns.index
        )
        return prices
    
    def test_sharpe_ratio(self, risk_calculator, sample_returns):
        """Test Sharpe ratio calculation."""
        sharpe = risk_calculator.calculate_sharpe_ratio(sample_returns)
        assert isinstance(sharpe, float)
        assert sharpe > 0
    
    def test_sortino_ratio(self, risk_calculator, sample_returns):
        """Test Sortino ratio calculation."""
        sortino = risk_calculator.calculate_sortino_ratio(sample_returns)
        assert isinstance(sortino, float)
    
    def test_max_drawdown(self, risk_calculator, sample_prices):
        """Test maximum drawdown calculation."""
        drawdown_info = risk_calculator.calculate_max_drawdown(sample_prices)
        
        assert isinstance(drawdown_info, dict)
        assert 'max_drawdown' in drawdown_info
        assert 'peak_date' in drawdown_info
        assert 'trough_date' in drawdown_info
        assert drawdown_info['max_drawdown'] <= 0
    
    def test_var_calculation(self, risk_calculator, sample_returns):
        """Test Value at Risk calculation."""
        var_95 = risk_calculator.calculate_var(sample_returns, 0.05, "historical")
        var_99 = risk_calculator.calculate_var(sample_returns, 0.01, "parametric")
        
        assert isinstance(var_95, dict)
        assert isinstance(var_99, dict)
        assert 'var_5%' in var_95
        assert 'var_1%' in var_99
        assert var_95['var_5%'] < 0
        assert var_99['var_1%'] < var_95['var_5%']  # 99% VaR should be more extreme
    
    def test_beta_calculation(self, risk_calculator, sample_returns):
        """Test beta calculation."""
        market_returns = sample_returns * 0.8 + np.random.normal(0, 0.01, len(sample_returns))
        market_returns.index = sample_returns.index
        
        beta = risk_calculator.calculate_beta(sample_returns, market_returns)
        assert isinstance(beta, float)
    
    def test_alpha_calculation(self, risk_calculator, sample_returns):
        """Test alpha calculation."""
        market_returns = sample_returns * 0.8 + np.random.normal(0, 0.01, len(sample_returns))
        market_returns.index = sample_returns.index
        
        alpha = risk_calculator.calculate_alpha(sample_returns, market_returns)
        assert isinstance(alpha, float)
    
    def test_comprehensive_risk_analysis(self, risk_calculator, sample_returns, sample_prices):
        """Test comprehensive risk analysis."""
        analysis = risk_calculator.comprehensive_risk_analysis(sample_returns, sample_prices)
        
        assert isinstance(analysis, dict)
        assert 'sharpe_ratio' in analysis
        assert 'sortino_ratio' in analysis
        assert 'drawdown_analysis' in analysis
        assert 'var_95%' in analysis
        assert 'return_statistics' in analysis


class TestDataLoader:
    """Test cases for DataLoader class."""
    
    @pytest.fixture
    def data_loader(self):
        """Create data loader instance."""
        return DataLoader()
    
    @patch('yfinance.download')
    def test_download_stock_data(self, mock_download, data_loader):
        """Test stock data download."""
        # Mock yfinance response
        mock_data = pd.DataFrame({
            'Adj Close': {
                'AAPL': [150, 151, 152],
                'MSFT': [300, 301, 302]
            }
        }, index=pd.date_range('2023-01-01', periods=3))
        mock_download.return_value = mock_data
        
        tickers = ["AAPL", "MSFT"]
        result = data_loader.download_stock_data(tickers, period="1y")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 2
        assert list(result.columns) == tickers
    
    def test_get_returns(self, data_loader):
        """Test returns calculation."""
        # Create sample price data
        prices = pd.DataFrame({
            'AAPL': [100, 101, 102, 103],
            'MSFT': [200, 201, 202, 203]
        })
        
        data_loader.data = prices
        
        # Test simple returns
        simple_returns = data_loader.get_returns(method='simple')
        assert isinstance(simple_returns, pd.DataFrame)
        assert len(simple_returns) == len(prices) - 1
        
        # Test log returns
        log_returns = data_loader.get_returns(method='log')
        assert isinstance(log_returns, pd.DataFrame)
        assert len(log_returns) == len(prices) - 1


class TestFeatureEngineer:
    """Test cases for FeatureEngineer class."""
    
    @pytest.fixture
    def feature_engineer(self):
        """Create feature engineer instance."""
        return FeatureEngineer()
    
    @pytest.fixture
    def sample_prices(self):
        """Create sample price data."""
        dates = pd.date_range('2023-01-01', periods=100)
        prices = pd.DataFrame({
            'AAPL': np.random.uniform(100, 200, 100),
            'MSFT': np.random.uniform(200, 300, 100)
        }, index=dates)
        return prices
    
    def test_calculate_returns(self, feature_engineer, sample_prices):
        """Test returns calculation."""
        returns = feature_engineer.calculate_returns(sample_prices)
        
        assert isinstance(returns, pd.DataFrame)
        assert len(returns.columns) == 4  # 2 tickers * 2 return types
        assert all(col.endswith('_return') for col in returns.columns)
    
    def test_calculate_volatility(self, feature_engineer, sample_prices):
        """Test volatility calculation."""
        returns = feature_engineer.calculate_returns(sample_prices)
        volatility = feature_engineer.calculate_volatility(returns)
        
        assert isinstance(volatility, pd.DataFrame)
        assert len(volatility.columns) == 2  # 2 tickers
        assert all('volatility' in col for col in volatility.columns)
    
    def test_calculate_moving_averages(self, feature_engineer, sample_prices):
        """Test moving averages calculation."""
        ma = feature_engineer.calculate_moving_averages(sample_prices)
        
        assert isinstance(ma, pd.DataFrame)
        assert len(ma.columns) == 12  # 2 tickers * 3 windows * 2 types
        assert all('sma' in col for col in ma.columns)
    
    def test_create_feature_matrix(self, feature_engineer, sample_prices):
        """Test feature matrix creation."""
        features = feature_engineer.create_feature_matrix(sample_prices)
        
        assert isinstance(features, pd.DataFrame)
        assert len(features) < len(sample_prices)  # Due to NaN removal
        assert len(features.columns) > 0
        assert not features.isnull().any().any()  # No NaN values


class TestReturnPredictor:
    """Test cases for ReturnPredictor class."""
    
    @pytest.fixture
    def predictor(self):
        """Create return predictor instance."""
        from return_predictor import ModelConfig
        config = ModelConfig(random_state=42, n_estimators=10)  # Small for testing
        return ReturnPredictor(config)
    
    @pytest.fixture
    def sample_features(self):
        """Create sample feature data."""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=200)
        
        # Create features for one ticker
        features = pd.DataFrame({
            'AAPL_simple_return': np.random.normal(0, 0.02, 200),
            'AAPL_volatility_20d': np.random.uniform(0.1, 0.3, 200),
            'AAPL_rsi_14': np.random.uniform(20, 80, 200),
            'AAPL_momentum_5d': np.random.normal(0, 0.05, 200),
            'AAPL_macd': np.random.normal(0, 0.01, 200)
        }, index=dates)
        
        return features
    
    @pytest.fixture
    def sample_target(self, sample_features):
        """Create sample target data."""
        target = sample_features['AAPL_simple_return'].shift(-1).dropna()
        return target
    
    def test_prepare_data(self, predictor, sample_features, sample_target):
        """Test data preparation."""
        X_train, X_test, y_train, y_test = predictor.prepare_data(
            sample_features, sample_target, scale_features=True
        )
        
        assert X_train.shape[0] > 0
        assert X_test.shape[0] > 0
        assert X_train.shape[1] == sample_features.shape[1]
        assert X_test.shape[1] == sample_features.shape[1]
        assert len(y_train) == X_train.shape[0]
        assert len(y_test) == X_test.shape[0]
    
    def test_train_random_forest(self, predictor, sample_features, sample_target):
        """Test Random Forest training."""
        result = predictor.train_random_forest(sample_features, sample_target, "test_rf")
        
        assert 'model' in result
        assert 'train_metrics' in result
        assert 'test_metrics' in result
        assert 'feature_importance' in result
        assert 'test_rf' in predictor.models
    
    def test_train_xgboost(self, predictor, sample_features, sample_target):
        """Test XGBoost training."""
        result = predictor.train_xgboost(sample_features, sample_target, "test_xgb")
        
        assert 'model' in result
        assert 'train_metrics' in result
        assert 'test_metrics' in result
        assert 'feature_importance' in result
        assert 'test_xgb' in predictor.models
    
    def test_predict_returns(self, predictor, sample_features, sample_target):
        """Test return prediction."""
        # Train a model first
        predictor.train_random_forest(sample_features, sample_target, "test_rf")
        
        # Make predictions
        latest_features = sample_features.iloc[-1:].copy()
        predictions = predictor.predict_returns(latest_features, "test_rf")
        
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 1
        assert 'test_rf' in predictor.predictions


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
