"""
Data Loader Module

This module handles downloading and loading stock price data using yfinance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """
    A class for downloading and managing stock price data.
    """
    
    def __init__(self):
        """
        Initialize the DataLoader.
        """
        self.data = None
        self.tickers = None
        
    def download_stock_data(
        self, 
        tickers: List[str], 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "5y"
    ) -> pd.DataFrame:
        """
        Download historical stock price data for given tickers.
        
        Args:
            tickers: List of stock ticker symbols
            start_date: Start date in 'YYYY-MM-DD' format (optional)
            end_date: End date in 'YYYY-MM-DD' format (optional)
            period: Time period if start_date and end_date not provided
                   (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
        Returns:
            DataFrame with adjusted close prices for all tickers
        """
        try:
            logger.info(f"Downloading data for tickers: {tickers}")
            
            # If specific dates are provided, use them
            if start_date and end_date:
                data = yf.download(
                    tickers, 
                    start=start_date, 
                    end=end_date,
                    progress=False
                )
            else:
                # Use period approach
                data = yf.download(
                    tickers, 
                    period=period,
                    progress=False
                )
            
            # Extract adjusted close prices
            if 'Adj Close' in data.columns:
                adj_close = data['Adj Close']
            elif 'Close' in data.columns:
                adj_close = data['Close']
            else:
                raise ValueError("No price data found in the downloaded data")
            
            # Handle single ticker case
            if len(tickers) == 1:
                adj_close = adj_close.to_frame()
                adj_close.columns = tickers
            
            # Remove any columns with all NaN values
            adj_close = adj_close.dropna(axis=1, how='all')
            
            # Forward fill missing values
            adj_close = adj_close.fillna(method='ffill')
            
            # Drop remaining NaN rows
            adj_close = adj_close.dropna()
            
            self.data = adj_close
            self.tickers = list(adj_close.columns)
            
            logger.info(f"Successfully downloaded data for {len(self.tickers)} tickers")
            logger.info(f"Data shape: {adj_close.shape}")
            
            return adj_close
            
        except Exception as e:
            logger.error(f"Error downloading stock data: {str(e)}")
            raise
    
    def get_returns(self, method: str = 'simple') -> pd.DataFrame:
        """
        Calculate returns from price data.
        
        Args:
            method: 'simple' for simple returns, 'log' for log returns
        
        Returns:
            DataFrame with calculated returns
        """
        if self.data is None:
            raise ValueError("No data available. Please download data first.")
        
        if method == 'simple':
            returns = self.data.pct_change()
        elif method == 'log':
            returns = np.log(self.data / self.data.shift(1))
        else:
            raise ValueError("Method must be 'simple' or 'log'")
        
        return returns.dropna()
    
    def validate_data_quality(self, min_data_points: int = 252) -> Dict[str, Any]:
        """
        Validate the quality of downloaded data.
        
        Args:
            min_data_points: Minimum number of data points required per ticker
        
        Returns:
            Dictionary with data quality metrics
        """
        if self.data is None:
            raise ValueError("No data available for validation")
        
        quality_report = {
            'total_tickers': len(self.tickers),
            'data_points': len(self.data),
            'date_range': {
                'start': self.data.index[0].strftime('%Y-%m-%d'),
                'end': self.data.index[-1].strftime('%Y-%m-%d')
            },
            'missing_data': {},
            'data_quality': 'good'
        }
        
        # Check for missing data per ticker
        for ticker in self.tickers:
            missing_count = self.data[ticker].isna().sum()
            total_count = len(self.data)
            missing_percentage = (missing_count / total_count) * 100
            
            quality_report['missing_data'][ticker] = {
                'missing_count': missing_count,
                'missing_percentage': missing_percentage
            }
            
            # Flag poor quality data
            if missing_percentage > 5 or total_count < min_data_points:
                quality_report['data_quality'] = 'poor'
        
        return quality_report
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded data.
        
        Returns:
            Dictionary with data information
        """
        if self.data is None:
            return {"status": "No data loaded"}
        
        return {
            "tickers": self.tickers,
            "shape": self.data.shape,
            "date_range": {
                "start": self.data.index[0].strftime('%Y-%m-%d'),
                "end": self.data.index[-1].strftime('%Y-%m-%d')
            },
            "data_types": self.data.dtypes.to_dict(),
            "null_counts": self.data.isnull().sum().to_dict()
        }


def load_sample_data() -> pd.DataFrame:
    """
    Load sample data for testing purposes.
    
    Returns:
        Sample DataFrame with stock prices
    """
    # Create sample data for demonstration
    np.random.seed(42)
    dates = pd.date_range(start='2019-01-01', end='2024-01-01', freq='D')
    
    # Generate synthetic price data
    tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN']
    data = {}
    
    for ticker in tickers:
        # Generate realistic price movements
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = [100]  # Starting price
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        data[ticker] = prices
    
    df = pd.DataFrame(data, index=dates)
    return df


if __name__ == "__main__":
    # Example usage
    loader = DataLoader()
    
    # Download data for example tickers
    tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
    data = loader.download_stock_data(tickers, period="2y")
    
    print("Data shape:", data.shape)
    print("Data head:")
    print(data.head())
    
    # Get data quality report
    quality = loader.validate_data_quality()
    print("\nData Quality Report:")
    print(quality)
