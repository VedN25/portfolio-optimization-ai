"""
Portfolio Optimizer Module

This module implements Modern Portfolio Theory optimization using scipy.optimize.
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """
    Results from portfolio optimization.
    """
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    success: bool
    message: str


class PortfolioOptimizer:
    """
    A class for optimizing portfolios using Modern Portfolio Theory.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize the PortfolioOptimizer.
        
        Args:
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
        self.expected_returns = None
        self.covariance_matrix = None
        self.tickers = None
        self.optimization_result = None
        
    def set_inputs(
        self, 
        expected_returns: Dict[str, float],
        covariance_matrix: pd.DataFrame
    ) -> None:
        """
        Set the inputs for optimization.
        
        Args:
            expected_returns: Dictionary of expected returns by ticker
            covariance_matrix: Covariance matrix of returns
        """
        self.expected_returns = expected_returns
        self.covariance_matrix = covariance_matrix
        self.tickers = list(expected_returns.keys())
        
        # Validate inputs
        if len(expected_returns) != len(covariance_matrix):
            raise ValueError("Number of expected returns must match covariance matrix dimensions")
        
        if set(self.tickers) != set(covariance_matrix.columns):
            raise ValueError("Ticker names must match between expected returns and covariance matrix")
        
        logger.info(f"Portfolio optimizer initialized with {len(self.tickers)} assets")
    
    def calculate_portfolio_metrics(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate portfolio metrics for given weights.
        
        Args:
            weights: Portfolio weights
        
        Returns:
            Tuple of (expected_return, volatility, sharpe_ratio)
        """
        # Convert expected returns to array
        returns_array = np.array([self.expected_returns[ticker] for ticker in self.tickers])
        
        # Calculate portfolio expected return
        portfolio_return = np.sum(weights * returns_array)
        
        # Calculate portfolio volatility
        portfolio_variance = np.dot(weights.T, np.dot(self.covariance_matrix.values, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Calculate Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return portfolio_return, portfolio_volatility, sharpe_ratio
    
    def negative_sharpe_ratio(self, weights: np.ndarray) -> float:
        """
        Calculate negative Sharpe ratio for minimization.
        
        Args:
            weights: Portfolio weights
        
        Returns:
            Negative Sharpe ratio
        """
        _, _, sharpe_ratio = self.calculate_portfolio_metrics(weights)
        return -sharpe_ratio
    
    def optimize_max_sharpe(self, weight_bounds: Tuple[float, float] = (0.0, 1.0)) -> OptimizationResult:
        """
        Optimize portfolio to maximize Sharpe ratio.
        
        Args:
            weight_bounds: Bounds for individual weights (min, max)
        
        Returns:
            OptimizationResult with optimal weights and metrics
        """
        if self.expected_returns is None or self.covariance_matrix is None:
            raise ValueError("Expected returns and covariance matrix must be set first")
        
        num_assets = len(self.tickers)
        
        # Constraints
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        
        # Bounds for each weight
        bounds = tuple(weight_bounds for _ in range(num_assets))
        
        # Initial guess (equal weights)
        initial_guess = np.array([1.0 / num_assets] * num_assets)
        
        logger.info("Starting Sharpe ratio optimization...")
        
        # Optimize
        result = minimize(
            self.negative_sharpe_ratio,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'disp': False}
        )
        
        if result.success:
            optimal_weights = result.x
            expected_return, volatility, sharpe_ratio = self.calculate_portfolio_metrics(optimal_weights)
            
            # Convert to dictionary
            weights_dict = dict(zip(self.tickers, optimal_weights))
            
            self.optimization_result = OptimizationResult(
                weights=weights_dict,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                success=True,
                message="Optimization successful"
            )
            
            logger.info(f"Optimization successful. Sharpe ratio: {sharpe_ratio:.4f}")
            
        else:
            self.optimization_result = OptimizationResult(
                weights={},
                expected_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                success=False,
                message=f"Optimization failed: {result.message}"
            )
            
            logger.error(f"Optimization failed: {result.message}")
        
        return self.optimization_result
    
    def optimize_min_volatility(self, weight_bounds: Tuple[float, float] = (0.0, 1.0)) -> OptimizationResult:
        """
        Optimize portfolio to minimize volatility.
        
        Args:
            weight_bounds: Bounds for individual weights (min, max)
        
        Returns:
            OptimizationResult with optimal weights and metrics
        """
        if self.expected_returns is None or self.covariance_matrix is None:
            raise ValueError("Expected returns and covariance matrix must be set first")
        
        num_assets = len(self.tickers)
        
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.covariance_matrix.values, weights)))
        
        # Constraints
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        
        # Bounds for each weight
        bounds = tuple(weight_bounds for _ in range(num_assets))
        
        # Initial guess (equal weights)
        initial_guess = np.array([1.0 / num_assets] * num_assets)
        
        logger.info("Starting minimum volatility optimization...")
        
        # Optimize
        result = minimize(
            portfolio_volatility,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'disp': False}
        )
        
        if result.success:
            optimal_weights = result.x
            expected_return, volatility, sharpe_ratio = self.calculate_portfolio_metrics(optimal_weights)
            
            # Convert to dictionary
            weights_dict = dict(zip(self.tickers, optimal_weights))
            
            result_obj = OptimizationResult(
                weights=weights_dict,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                success=True,
                message="Min volatility optimization successful"
            )
            
            logger.info(f"Min volatility optimization successful. Volatility: {volatility:.4f}")
            return result_obj
            
        else:
            logger.error(f"Min volatility optimization failed: {result.message}")
            return OptimizationResult(
                weights={},
                expected_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                success=False,
                message=f"Min volatility optimization failed: {result.message}"
            )
    
    def optimize_equal_weight(self) -> OptimizationResult:
        """
        Create an equal-weight portfolio.
        
        Returns:
            OptimizationResult with equal weights and metrics
        """
        if self.expected_returns is None or self.covariance_matrix is None:
            raise ValueError("Expected returns and covariance matrix must be set first")
        
        num_assets = len(self.tickers)
        equal_weights = np.array([1.0 / num_assets] * num_assets)
        
        expected_return, volatility, sharpe_ratio = self.calculate_portfolio_metrics(equal_weights)
        
        # Convert to dictionary
        weights_dict = dict(zip(self.tickers, equal_weights))
        
        result = OptimizationResult(
            weights=weights_dict,
            expected_return=expected_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            success=True,
            message="Equal weight portfolio created"
        )
        
        logger.info("Equal weight portfolio created")
        
        return result
    
    def generate_efficient_frontier(self, num_portfolios: int = 100) -> pd.DataFrame:
        """
        Generate the efficient frontier.
        
        Args:
            num_portfolios: Number of portfolios to generate
        
        Returns:
            DataFrame with efficient frontier points
        """
        if self.expected_returns is None or self.covariance_matrix is None:
            raise ValueError("Expected returns and covariance matrix must be set first")
        
        num_assets = len(self.tickers)
        
        # Find minimum and maximum returns
        min_vol_result = self.optimize_min_volatility()
        max_sharpe_result = self.optimize_max_sharpe()
        
        min_return = min_vol_result.expected_return
        max_return = max_sharpe_result.expected_return
        
        # Generate target returns
        target_returns = np.linspace(min_return, max_return, num_portfolios)
        
        efficient_portfolios = []
        
        for target_return in target_returns:
            try:
                # Optimize for minimum volatility given target return
                def portfolio_volatility(weights):
                    return np.sqrt(np.dot(weights.T, np.dot(self.covariance_matrix.values, weights)))
                
                def return_constraint(weights):
                    returns_array = np.array([self.expected_returns[ticker] for ticker in self.tickers])
                    return np.sum(weights * returns_array) - target_return
                
                constraints = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
                    {'type': 'eq', 'fun': return_constraint}  # Target return
                ]
                
                bounds = tuple((0.0, 1.0) for _ in range(num_assets))
                initial_guess = np.array([1.0 / num_assets] * num_assets)
                
                result = minimize(
                    portfolio_volatility,
                    initial_guess,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints,
                    options={'ftol': 1e-9, 'disp': False}
                )
                
                if result.success:
                    weights = result.x
                    volatility = portfolio_volatility(weights)
                    _, _, sharpe_ratio = self.calculate_portfolio_metrics(weights)
                    
                    efficient_portfolios.append({
                        'return': target_return,
                        'volatility': volatility,
                        'sharpe_ratio': sharpe_ratio,
                        'weights': dict(zip(self.tickers, weights))
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to generate portfolio for return {target_return}: {str(e)}")
                continue
        
        return pd.DataFrame(efficient_portfolios)
    
    def monte_carlo_simulation(self, num_portfolios: int = 10000) -> pd.DataFrame:
        """
        Generate random portfolios using Monte Carlo simulation.
        
        Args:
            num_portfolios: Number of random portfolios to generate
        
        Returns:
            DataFrame with random portfolio results
        """
        if self.expected_returns is None or self.covariance_matrix is None:
            raise ValueError("Expected returns and covariance matrix must be set first")
        
        num_assets = len(self.tickers)
        
        results = []
        
        for _ in range(num_portfolios):
            # Generate random weights
            weights = np.random.random(num_assets)
            weights = weights / np.sum(weights)  # Normalize to sum to 1
            
            # Calculate portfolio metrics
            expected_return, volatility, sharpe_ratio = self.calculate_portfolio_metrics(weights)
            
            results.append({
                'return': expected_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'weights': dict(zip(self.tickers, weights))
            })
        
        return pd.DataFrame(results)
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the optimization results.
        
        Returns:
            Dictionary with portfolio summary
        """
        if self.optimization_result is None:
            return {"status": "No optimization performed"}
        
        result = self.optimization_result
        
        # Calculate additional metrics
        weights_array = np.array([result.weights[ticker] for ticker in self.tickers])
        
        # Portfolio beta (assuming market beta of 1 for all assets)
        portfolio_beta = np.sum(weights_array * np.ones(len(self.tickers)))
        
        # Diversification ratio
        weighted_volatilities = np.sqrt(np.diag(self.covariance_matrix.values))
        portfolio_volatility = result.volatility
        diversification_ratio = np.sum(weights_array * weighted_volatilities) / portfolio_volatility
        
        return {
            'optimization_success': result.success,
            'message': result.message,
            'expected_return': result.expected_return,
            'volatility': result.volatility,
            'sharpe_ratio': result.sharpe_ratio,
            'portfolio_beta': portfolio_beta,
            'diversification_ratio': diversification_ratio,
            'num_assets': len(self.tickers),
            'weights': result.weights,
            'top_holdings': sorted(result.weights.items(), key=lambda x: x[1], reverse=True)[:5]
        }


if __name__ == "__main__":
    # Example usage
    # Create sample data
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
    
    # Optimize portfolio
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    optimizer.set_inputs(expected_returns, cov_matrix)
    
    # Max Sharpe ratio optimization
    result = optimizer.optimize_max_sharpe()
    print("Max Sharpe Portfolio:")
    print(f"Expected Return: {result.expected_return:.4f}")
    print(f"Volatility: {result.volatility:.4f}")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.4f}")
    print("Weights:", result.weights)
    
    # Get portfolio summary
    summary = optimizer.get_portfolio_summary()
    print("\nPortfolio Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
