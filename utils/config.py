"""
Configuration Module

This module contains configuration settings for the portfolio optimization system.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///portfolio_optimization.db"
    echo: bool = False


@dataclass
class APIConfig:
    """API configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = field(default_factory=lambda: ["*"])
    max_workers: int = 4
    timeout: int = 300


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    host: str = "localhost"
    port: int = 8501
    debug: bool = False


@dataclass
class DataConfig:
    """Data configuration."""
    default_period: str = "5y"
    cache_dir: str = "data/cache"
    max_tickers_per_request: int = 50
    min_data_points: int = 252
    data_quality_threshold: float = 0.95


@dataclass
class ModelConfig:
    """Machine learning model configuration."""
    random_state: int = 42
    test_size: float = 0.2
    n_splits: int = 5
    
    # RandomForest parameters
    rf_n_estimators: int = 100
    rf_max_depth: Optional[int] = None
    rf_min_samples_split: int = 2
    rf_min_samples_leaf: int = 1
    
    # XGBoost parameters
    xgb_n_estimators: int = 100
    xgb_max_depth: int = 6
    xgb_learning_rate: float = 0.1
    xgb_subsample: float = 0.8
    xgb_colsample_bytree: float = 0.8
    
    # Feature engineering
    ma_windows: list = field(default_factory=lambda: [10, 20, 50])
    rsi_window: int = 14
    momentum_periods: list = field(default_factory=lambda: [5, 10, 20])
    bb_window: int = 20
    bb_num_std: float = 2.0
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9


@dataclass
class OptimizationConfig:
    """Portfolio optimization configuration."""
    risk_free_rate: float = 0.02
    optimization_method: str = "max_sharpe"
    weight_bounds: tuple = (0.0, 1.0)
    enable_ml_prediction: bool = True
    
    # Monte Carlo simulation
    monte_carlo_portfolios: int = 10000
    
    # Efficient frontier
    efficient_frontier_points: int = 100
    
    # Constraints
    min_weight_per_asset: float = 0.0
    max_weight_per_asset: float = 1.0
    max_concentration: float = 0.4  # Maximum weight for any single asset


@dataclass
class RiskConfig:
    """Risk metrics configuration."""
    confidence_levels: list = field(default_factory=lambda: [0.05, 0.01])
    var_methods: list = field(default_factory=lambda: ["historical", "parametric"])
    monte_carlo_simulations: int = 10000
    lookback_period: int = 252  # Trading days


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class CacheConfig:
    """Caching configuration."""
    enabled: bool = True
    ttl: int = 3600  # 1 hour
    max_size: int = 1000
    cache_dir: str = "cache"


class Config:
    """
    Main configuration class that loads settings from environment variables
    and provides access to all configuration sections.
    """
    
    def __init__(self):
        """Initialize configuration."""
        # Load environment variables
        self._load_env_vars()
        
        # Initialize configuration sections
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.dashboard = DashboardConfig()
        self.data = DataConfig()
        self.model = ModelConfig()
        self.optimization = OptimizationConfig()
        self.risk = RiskConfig()
        self.logging = LoggingConfig()
        self.cache = CacheConfig()
        
        # Override with environment variables
        self._override_from_env()
    
    def _load_env_vars(self):
        """Load environment variables."""
        pass
    
    def _override_from_env(self):
        """Override configuration with environment variables."""
        # API Configuration
        if os.getenv("API_HOST"):
            self.api.host = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            self.api.port = int(os.getenv("API_PORT"))
        if os.getenv("API_DEBUG"):
            self.api.debug = os.getenv("API_DEBUG").lower() == "true"
        
        # Dashboard Configuration
        if os.getenv("DASHBOARD_HOST"):
            self.dashboard.host = os.getenv("DASHBOARD_HOST")
        if os.getenv("DASHBOARD_PORT"):
            self.dashboard.port = int(os.getenv("DASHBOARD_PORT"))
        
        # Data Configuration
        if os.getenv("DATA_PERIOD"):
            self.data.default_period = os.getenv("DATA_PERIOD")
        if os.getenv("CACHE_DIR"):
            self.data.cache_dir = os.getenv("CACHE_DIR")
        
        # Model Configuration
        if os.getenv("RF_N_ESTIMATORS"):
            self.model.rf_n_estimators = int(os.getenv("RF_N_ESTIMATORS"))
        if os.getenv("XGB_N_ESTIMATORS"):
            self.model.xgb_n_estimators = int(os.getenv("XGB_N_ESTIMATORS"))
        
        # Optimization Configuration
        if os.getenv("RISK_FREE_RATE"):
            self.optimization.risk_free_rate = float(os.getenv("RISK_FREE_RATE"))
        if os.getenv("OPTIMIZATION_METHOD"):
            self.optimization.optimization_method = os.getenv("OPTIMIZATION_METHOD")
        
        # Logging Configuration
        if os.getenv("LOG_LEVEL"):
            self.logging.level = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            self.logging.file_path = os.getenv("LOG_FILE")
    
    def get_database_url(self) -> str:
        """Get database URL."""
        return self.database.url
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration as dictionary."""
        return {
            "host": self.api.host,
            "port": self.api.port,
            "debug": self.api.debug,
            "cors_origins": self.api.cors_origins
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration as dictionary."""
        return {
            "random_state": self.model.random_state,
            "test_size": self.model.test_size,
            "n_splits": self.model.n_splits,
            "rf_n_estimators": self.model.rf_n_estimators,
            "rf_max_depth": self.model.rf_max_depth,
            "rf_min_samples_split": self.model.rf_min_samples_split,
            "rf_min_samples_leaf": self.model.rf_min_samples_leaf,
            "xgb_n_estimators": self.model.xgb_n_estimators,
            "xgb_max_depth": self.model.xgb_max_depth,
            "xgb_learning_rate": self.model.xgb_learning_rate,
            "xgb_subsample": self.model.xgb_subsample,
            "xgb_colsample_bytree": self.model.xgb_colsample_bytree
        }
    
    def get_optimization_config(self) -> Dict[str, Any]:
        """Get optimization configuration as dictionary."""
        return {
            "risk_free_rate": self.optimization.risk_free_rate,
            "optimization_method": self.optimization.optimization_method,
            "weight_bounds": self.optimization.weight_bounds,
            "enable_ml_prediction": self.optimization.enable_ml_prediction,
            "monte_carlo_portfolios": self.optimization.monte_carlo_portfolios,
            "efficient_frontier_points": self.optimization.efficient_frontier_points
        }
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration as dictionary."""
        return {
            "default_period": self.data.default_period,
            "cache_dir": self.data.cache_dir,
            "max_tickers_per_request": self.data.max_tickers_per_request,
            "min_data_points": self.data.min_data_points,
            "data_quality_threshold": self.data.data_quality_threshold
        }
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        # Validate API configuration
        if not (1 <= self.api.port <= 65535):
            errors.append("API port must be between 1 and 65535")
        
        # Validate dashboard configuration
        if not (1 <= self.dashboard.port <= 65535):
            errors.append("Dashboard port must be between 1 and 65535")
        
        # Validate data configuration
        if self.data.default_period not in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]:
            errors.append("Invalid data period")
        
        # Validate optimization configuration
        if self.optimization.optimization_method not in ["max_sharpe", "min_volatility", "equal_weight"]:
            errors.append("Invalid optimization method")
        
        if not (0 <= self.optimization.risk_free_rate <= 1):
            errors.append("Risk-free rate must be between 0 and 1")
        
        # Validate model configuration
        if self.model.rf_n_estimators <= 0:
            errors.append("Random Forest n_estimators must be positive")
        
        if self.model.xgb_n_estimators <= 0:
            errors.append("XGBoost n_estimators must be positive")
        
        if errors:
            raise ValueError("Configuration validation failed: " + "; ".join(errors))
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "database": self.database.__dict__,
            "api": self.api.__dict__,
            "dashboard": self.dashboard.__dict__,
            "data": self.data.__dict__,
            "model": self.model.__dict__,
            "optimization": self.optimization.__dict__,
            "risk": self.risk.__dict__,
            "logging": self.logging.__dict__,
            "cache": self.cache.__dict__
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get global configuration instance."""
    return config


def load_config_from_file(config_path: str) -> Config:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Loaded configuration
    """
    import json
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    # Create new config instance
    new_config = Config()
    
    # Override settings from file
    if "database" in config_data:
        for key, value in config_data["database"].items():
            setattr(new_config.database, key, value)
    
    if "api" in config_data:
        for key, value in config_data["api"].items():
            setattr(new_config.api, key, value)
    
    if "model" in config_data:
        for key, value in config_data["model"].items():
            setattr(new_config.model, key, value)
    
    if "optimization" in config_data:
        for key, value in config_data["optimization"].items():
            setattr(new_config.optimization, key, value)
    
    return new_config


if __name__ == "__main__":
    # Test configuration
    try:
        config.validate()
        print("Configuration is valid")
        
        # Print configuration
        print("\nConfiguration:")
        print(json.dumps(config.to_dict(), indent=2))
        
    except Exception as e:
        print(f"Configuration error: {e}")
