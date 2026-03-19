"""
Risk Metrics Module

This module calculates various risk metrics for portfolio analysis.
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class RiskMetrics:
    """
    A class for calculating portfolio risk metrics.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize the RiskMetrics.
        
        Args:
            risk_free_rate: Risk-free rate for calculations
        """
        self.risk_free_rate = risk_free_rate
        
    def calculate_sharpe_ratio(
        self, 
        returns: pd.Series, 
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Series of portfolio returns
            risk_free_rate: Risk-free rate (uses instance default if None)
        
        Returns:
            Sharpe ratio
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Annualize returns and volatility
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        
        if annual_volatility == 0:
            return 0.0
        
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        return sharpe_ratio
    
    def calculate_sortino_ratio(
        self, 
        returns: pd.Series, 
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sortino ratio (downside risk-adjusted return).
        
        Args:
            returns: Series of portfolio returns
            risk_free_rate: Risk-free rate (uses instance default if None)
        
        Returns:
            Sortino ratio
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Annualize returns
        annual_return = returns.mean() * 252
        
        # Calculate downside deviation
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252)
        
        if downside_deviation == 0:
            return 0.0
        
        sortino_ratio = (annual_return - risk_free_rate) / downside_deviation
        return sortino_ratio
    
    def calculate_max_drawdown(self, prices: pd.Series) -> Dict[str, Any]:
        """
        Calculate maximum drawdown and related metrics.
        
        Args:
            prices: Series of portfolio prices
        
        Returns:
            Dictionary with drawdown metrics
        """
        # Calculate cumulative returns
        cumulative_returns = (1 + prices.pct_change()).cumprod()
        
        # Calculate running maximum
        running_max = cumulative_returns.expanding().max()
        
        # Calculate drawdown
        drawdown = (cumulative_returns - running_max) / running_max
        
        # Maximum drawdown
        max_drawdown = drawdown.min()
        
        # Find the dates of max drawdown
        max_dd_date = drawdown.idxmin()
        
        # Find the peak before max drawdown
        peak_date = cumulative_returns.loc[:max_dd_date].idxmax()
        
        # Calculate duration of drawdown
        drawdown_duration = (max_dd_date - peak_date).days
        
        # Calculate time to recover (if recovered)
        recovery_date = None
        recovery_duration = None
        
        if max_dd_date < cumulative_returns.index[-1]:
            recovery_mask = cumulative_returns.loc[max_dd_date:] >= cumulative_returns.loc[peak_date]
            if recovery_mask.any():
                recovery_date = recovery_mask.idxmax()
                recovery_duration = (recovery_date - max_dd_date).days
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_percentage': abs(max_drawdown) * 100,
            'peak_date': peak_date,
            'trough_date': max_dd_date,
            'drawdown_duration_days': drawdown_duration,
            'recovery_date': recovery_date,
            'recovery_duration_days': recovery_duration,
            'current_drawdown': drawdown.iloc[-1] if len(drawdown) > 0 else 0.0
        }
    
    def calculate_var(
        self, 
        returns: pd.Series, 
        confidence_level: float = 0.05,
        method: str = "historical"
    ) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Series of portfolio returns
            confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
            method: Method for VaR calculation ("historical", "parametric", "monte_carlo")
        
        Returns:
            Dictionary with VaR metrics
        """
        if method == "historical":
            # Historical VaR
            var = returns.quantile(confidence_level)
            
        elif method == "parametric":
            # Parametric VaR (assuming normal distribution)
            mean = returns.mean()
            std = returns.std()
            var = norm.ppf(confidence_level, mean, std)
            
        elif method == "monte_carlo":
            # Monte Carlo VaR
            n_simulations = 10000
            mean = returns.mean()
            std = returns.std()
            
            # Generate random returns
            simulated_returns = np.random.normal(mean, std, n_simulations)
            var = np.percentile(simulated_returns, confidence_level * 100)
            
        else:
            raise ValueError(f"Unknown VaR method: {method}")
        
        # Calculate Expected Shortfall (CVaR)
        if method == "historical":
            expected_shortfall = returns[returns <= var].mean()
        elif method == "parametric":
            expected_shortfall = norm.ppf(confidence_level / 2, returns.mean(), returns.std())
        else:  # monte_carlo
            expected_shortfall = simulated_returns[simulated_returns <= var].mean()
        
        return {
            f'var_{confidence_level*100:.0f}%': var,
            f'var_{confidence_level*100:.0f}%_percentage': abs(var) * 100,
            f'expected_shortfall_{confidence_level*100:.0f}%': expected_shortfall,
            f'expected_shortfall_{confidence_level*100:.0f}%_percentage': abs(expected_shortfall) * 100
        }
    
    def calculate_beta(
        self, 
        portfolio_returns: pd.Series, 
        market_returns: pd.Series
    ) -> float:
        """
        Calculate portfolio beta relative to market.
        
        Args:
            portfolio_returns: Series of portfolio returns
            market_returns: Series of market returns
        
        Returns:
            Portfolio beta
        """
        # Align the series
        aligned_data = pd.concat([portfolio_returns, market_returns], axis=1).dropna()
        portfolio_aligned = aligned_data.iloc[:, 0]
        market_aligned = aligned_data.iloc[:, 1]
        
        # Calculate covariance and variance
        covariance = np.cov(portfolio_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        if market_variance == 0:
            return 1.0  # Default to market beta if no variance
        
        beta = covariance / market_variance
        return beta
    
    def calculate_alpha(
        self, 
        portfolio_returns: pd.Series, 
        market_returns: pd.Series,
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Jensen's alpha.
        
        Args:
            portfolio_returns: Series of portfolio returns
            market_returns: Series of market returns
            risk_free_rate: Risk-free rate (uses instance default if None)
        
        Returns:
            Jensen's alpha
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Calculate beta
        beta = self.calculate_beta(portfolio_returns, market_returns)
        
        # Calculate annualized returns
        portfolio_annual_return = portfolio_returns.mean() * 252
        market_annual_return = market_returns.mean() * 252
        
        # Calculate alpha
        alpha = portfolio_annual_return - (risk_free_rate + beta * (market_annual_return - risk_free_rate))
        
        return alpha
    
    def calculate_information_ratio(
        self, 
        portfolio_returns: pd.Series, 
        benchmark_returns: pd.Series
    ) -> float:
        """
        Calculate Information Ratio.
        
        Args:
            portfolio_returns: Series of portfolio returns
            benchmark_returns: Series of benchmark returns
        
        Returns:
            Information Ratio
        """
        # Calculate active returns
        active_returns = portfolio_returns - benchmark_returns
        
        # Calculate tracking error
        tracking_error = active_returns.std() * np.sqrt(252)
        
        if tracking_error == 0:
            return 0.0
        
        # Calculate information ratio
        information_ratio = active_returns.mean() * 252 / tracking_error
        
        return information_ratio
    
    def calculate_tracking_error(
        self, 
        portfolio_returns: pd.Series, 
        benchmark_returns: pd.Series
    ) -> float:
        """
        Calculate tracking error.
        
        Args:
            portfolio_returns: Series of portfolio returns
            benchmark_returns: Series of benchmark returns
        
        Returns:
            Tracking error
        """
        # Calculate active returns
        active_returns = portfolio_returns - benchmark_returns
        
        # Annualized tracking error
        tracking_error = active_returns.std() * np.sqrt(252)
        
        return tracking_error
    
    def calculate_calmar_ratio(self, returns: pd.Series, prices: pd.Series) -> float:
        """
        Calculate Calmar ratio (annualized return / maximum drawdown).
        
        Args:
            returns: Series of portfolio returns
            prices: Series of portfolio prices
        
        Returns:
            Calmar ratio
        """
        # Calculate annualized return
        annual_return = returns.mean() * 252
        
        # Calculate maximum drawdown
        max_dd_info = self.calculate_max_drawdown(prices)
        max_drawdown = abs(max_dd_info['max_drawdown'])
        
        if max_drawdown == 0:
            return 0.0
        
        calmar_ratio = annual_return / max_drawdown
        return calmar_ratio
    
    def calculate_omega_ratio(
        self, 
        returns: pd.Series, 
        threshold: float = 0.0
    ) -> float:
        """
        Calculate Omega ratio.
        
        Args:
            returns: Series of portfolio returns
            threshold: Threshold return (default 0)
        
        Returns:
            Omega ratio
        """
        # Separate gains and losses
        gains = returns[returns > threshold] - threshold
        losses = threshold - returns[returns <= threshold]
        
        if len(losses) == 0 or losses.sum() == 0:
            return float('inf') if len(gains) > 0 else 0.0
        
        omega_ratio = gains.sum() / losses.sum()
        return omega_ratio
    
    def comprehensive_risk_analysis(
        self, 
        returns: pd.Series, 
        prices: pd.Series,
        market_returns: Optional[pd.Series] = None,
        benchmark_returns: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive risk analysis.
        
        Args:
            returns: Series of portfolio returns
            prices: Series of portfolio prices
            market_returns: Series of market returns (optional)
            benchmark_returns: Series of benchmark returns (optional)
        
        Returns:
            Dictionary with comprehensive risk metrics
        """
        risk_analysis = {}
        
        # Basic metrics
        risk_analysis['sharpe_ratio'] = self.calculate_sharpe_ratio(returns)
        risk_analysis['sortino_ratio'] = self.calculate_sortino_ratio(returns)
        
        # Drawdown metrics
        risk_analysis['drawdown_analysis'] = self.calculate_max_drawdown(prices)
        
        # VaR metrics
        risk_analysis['var_95%'] = self.calculate_var(returns, 0.05, "historical")
        risk_analysis['var_99%'] = self.calculate_var(returns, 0.01, "historical")
        
        # Calmar ratio
        risk_analysis['calmar_ratio'] = self.calculate_calmar_ratio(returns, prices)
        
        # Omega ratio
        risk_analysis['omega_ratio'] = self.calculate_omega_ratio(returns)
        
        # Market-related metrics (if provided)
        if market_returns is not None:
            risk_analysis['beta'] = self.calculate_beta(returns, market_returns)
            risk_analysis['alpha'] = self.calculate_alpha(returns, market_returns)
        
        if benchmark_returns is not None:
            risk_analysis['information_ratio'] = self.calculate_information_ratio(returns, benchmark_returns)
            risk_analysis['tracking_error'] = self.calculate_tracking_error(returns, benchmark_returns)
        
        # Additional statistics
        risk_analysis['return_statistics'] = {
            'mean': returns.mean(),
            'std': returns.std(),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'min': returns.min(),
            'max': returns.max(),
            'annualized_return': returns.mean() * 252,
            'annualized_volatility': returns.std() * np.sqrt(252)
        }
        
        return risk_analysis


if __name__ == "__main__":
    # Example usage
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='D')
    
    # Generate sample returns
    returns = pd.Series(
        np.random.normal(0.0005, 0.02, len(dates)),
        index=dates
    )
    
    # Generate sample prices
    prices = pd.Series(
        100 * (1 + returns).cumprod(),
        index=dates
    )
    
    # Calculate risk metrics
    risk_calculator = RiskMetrics(risk_free_rate=0.02)
    
    # Comprehensive analysis
    analysis = risk_calculator.comprehensive_risk_analysis(returns, prices)
    
    print("Risk Analysis Results:")
    for key, value in analysis.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value:.4f}")
        else:
            print(f"{key}: {value:.4f}")
