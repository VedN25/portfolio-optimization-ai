"""
Feature Engineering Module

This module computes financial indicators and features for machine learning models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    A class for engineering financial features from stock price data.
    """
    
    def __init__(self):
        """
        Initialize the FeatureEngineer.
        """
        self.features = None
        self.price_data = None
        
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate simple and log returns.
        
        Args:
            prices: DataFrame with stock prices
        
        Returns:
            DataFrame with simple and log returns
        """
        returns_dict = {}
        
        for ticker in prices.columns:
            # Simple returns
            simple_returns = prices[ticker].pct_change()
            
            # Log returns
            log_returns = np.log(prices[ticker] / prices[ticker].shift(1))
            
            returns_dict[f'{ticker}_simple_return'] = simple_returns
            returns_dict[f'{ticker}_log_return'] = log_returns
        
        return pd.DataFrame(returns_dict)
    
    def calculate_volatility(self, returns: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Calculate rolling volatility.
        
        Args:
            returns: DataFrame with returns
            window: Rolling window size
        
        Returns:
            DataFrame with rolling volatility
        """
        volatility_dict = {}
        
        for ticker in returns.columns:
            if '_return' in ticker:
                base_ticker = ticker.split('_')[0]
                rolling_vol = returns[ticker].rolling(window=window).std() * np.sqrt(252)
                volatility_dict[f'{base_ticker}_volatility_{window}d'] = rolling_vol
        
        return pd.DataFrame(volatility_dict)
    
    def calculate_moving_averages(self, prices: pd.DataFrame, windows: List[int] = [10, 20, 50]) -> pd.DataFrame:
        """
        Calculate moving averages and price ratios.
        
        Args:
            prices: DataFrame with stock prices
            windows: List of moving average windows
        
        Returns:
            DataFrame with moving averages and ratios
        """
        ma_dict = {}
        
        for ticker in prices.columns:
            for window in windows:
                # Simple moving average
                sma = prices[ticker].rolling(window=window).mean()
                ma_dict[f'{ticker}_sma_{window}'] = sma
                
                # Price to SMA ratio
                price_sma_ratio = prices[ticker] / sma
                ma_dict[f'{ticker}_price_sma_ratio_{window}'] = price_sma_ratio
        
        return pd.DataFrame(ma_dict)
    
    def calculate_rsi(self, prices: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: DataFrame with stock prices
            window: RSI calculation window
        
        Returns:
            DataFrame with RSI values
        """
        rsi_dict = {}
        
        for ticker in prices.columns:
            delta = prices[ticker].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            rsi_dict[f'{ticker}_rsi_{window}'] = rsi
        
        return pd.DataFrame(rsi_dict)
    
    def calculate_momentum(self, prices: pd.DataFrame, periods: List[int] = [5, 10, 20]) -> pd.DataFrame:
        """
        Calculate momentum indicators.
        
        Args:
            prices: DataFrame with stock prices
            periods: List of momentum periods
        
        Returns:
            DataFrame with momentum indicators
        """
        momentum_dict = {}
        
        for ticker in prices.columns:
            for period in periods:
                # Price momentum (percentage change over period)
                momentum = prices[ticker].pct_change(period)
                momentum_dict[f'{ticker}_momentum_{period}d'] = momentum
                
                # Rate of change
                roc = ((prices[ticker] - prices[ticker].shift(period)) / prices[ticker].shift(period)) * 100
                momentum_dict[f'{ticker}_roc_{period}d'] = roc
        
        return pd.DataFrame(momentum_dict)
    
    def calculate_bollinger_bands(self, prices: pd.DataFrame, window: int = 20, num_std: float = 2) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: DataFrame with stock prices
            window: Moving average window
            num_std: Number of standard deviations
        
        Returns:
            DataFrame with Bollinger Bands
        """
        bb_dict = {}
        
        for ticker in prices.columns:
            sma = prices[ticker].rolling(window=window).mean()
            std = prices[ticker].rolling(window=window).std()
            
            upper_band = sma + (std * num_std)
            lower_band = sma - (std * num_std)
            
            # Band width
            band_width = (upper_band - lower_band) / sma
            
            # %B (position within bands)
            percent_b = (prices[ticker] - lower_band) / (upper_band - lower_band)
            
            bb_dict[f'{ticker}_bb_upper_{window}'] = upper_band
            bb_dict[f'{ticker}_bb_lower_{window}'] = lower_band
            bb_dict[f'{ticker}_bb_width_{window}'] = band_width
            bb_dict[f'{ticker}_bb_percent_b_{window}'] = percent_b
        
        return pd.DataFrame(bb_dict)
    
    def calculate_macd(self, prices: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: DataFrame with stock prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        
        Returns:
            DataFrame with MACD indicators
        """
        macd_dict = {}
        
        for ticker in prices.columns:
            ema_fast = prices[ticker].ewm(span=fast).mean()
            ema_slow = prices[ticker].ewm(span=slow).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            macd_dict[f'{ticker}_macd'] = macd_line
            macd_dict[f'{ticker}_macd_signal'] = signal_line
            macd_dict[f'{ticker}_macd_histogram'] = histogram
        
        return pd.DataFrame(macd_dict)
    
    def create_feature_matrix(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Create a comprehensive feature matrix from price data.
        
        Args:
            prices: DataFrame with stock prices
        
        Returns:
            DataFrame with all engineered features
        """
        logger.info("Creating feature matrix...")
        
        self.price_data = prices
        
        # Calculate returns
        returns = self.calculate_returns(prices)
        
        # Calculate volatility
        volatility = self.calculate_volatility(returns)
        
        # Calculate moving averages
        moving_averages = self.calculate_moving_averages(prices)
        
        # Calculate RSI
        rsi = self.calculate_rsi(prices)
        
        # Calculate momentum
        momentum = self.calculate_momentum(prices)
        
        # Calculate Bollinger Bands
        bollinger_bands = self.calculate_bollinger_bands(prices)
        
        # Calculate MACD
        macd = self.calculate_macd(prices)
        
        # Combine all features
        all_features = pd.concat([
            returns,
            volatility,
            moving_averages,
            rsi,
            momentum,
            bollinger_bands,
            macd
        ], axis=1)
        
        # Remove rows with NaN values
        all_features = all_features.dropna()
        
        self.features = all_features
        
        logger.info(f"Feature matrix created with shape: {all_features.shape}")
        
        return all_features
    
    def get_feature_importance_data(self, target_ticker: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare data for feature importance analysis.
        
        Args:
            target_ticker: Ticker to predict returns for
        
        Returns:
            Tuple of (features DataFrame, target Series)
        """
        if self.features is None:
            raise ValueError("No features available. Create feature matrix first.")
        
        # Get target variable (next day's simple return)
        target_col = f'{target_ticker}_simple_return'
        if target_col not in self.features.columns:
            raise ValueError(f"Target column {target_col} not found in features")
        
        # Shift target to predict next day's return
        target = self.features[target_col].shift(-1).dropna()
        
        # Align features with target
        features = self.features.loc[target.index].copy()
        
        # Remove target-related columns from features to avoid data leakage
        cols_to_remove = [col for col in features.columns if target_ticker in col]
        features = features.drop(columns=cols_to_remove)
        
        return features, target
    
    def get_feature_summary(self) -> Dict:
        """
        Get summary statistics of engineered features.
        
        Returns:
            Dictionary with feature summary
        """
        if self.features is None:
            return {"status": "No features available"}
        
        summary = {
            "total_features": len(self.features.columns),
            "feature_categories": {},
            "missing_values": self.features.isnull().sum().sum(),
            "data_points": len(self.features)
        }
        
        # Categorize features
        for col in self.features.columns:
            if '_return' in col:
                category = 'returns'
            elif '_volatility' in col:
                category = 'volatility'
            elif '_sma' in col or '_price_sma_ratio' in col:
                category = 'moving_averages'
            elif '_rsi' in col:
                category = 'rsi'
            elif '_momentum' in col or '_roc' in col:
                category = 'momentum'
            elif '_bb_' in col:
                category = 'bollinger_bands'
            elif '_macd' in col:
                category = 'macd'
            else:
                category = 'other'
            
            if category not in summary['feature_categories']:
                summary['feature_categories'][category] = 0
            summary['feature_categories'][category] += 1
        
        return summary


if __name__ == "__main__":
    # Example usage
    from data_loader import DataLoader
    
    # Load sample data
    loader = DataLoader()
    prices = loader.download_stock_data(["AAPL", "MSFT"], period="1y")
    
    # Create features
    engineer = FeatureEngineer()
    features = engineer.create_feature_matrix(prices)
    
    print("Feature matrix shape:", features.shape)
    print("Feature columns:", features.columns.tolist()[:10])  # Show first 10
    print("\nFeature summary:")
    print(engineer.get_feature_summary())
