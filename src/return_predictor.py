"""
Return Predictor Module

This module implements machine learning models to predict asset returns.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """
    Configuration for ML models.
    """
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


class ReturnPredictor:
    """
    A class for predicting asset returns using machine learning models.
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initialize the ReturnPredictor.
        
        Args:
            config: Model configuration
        """
        self.config = config or ModelConfig()
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.predictions = {}
        self.model_performance = {}
        
    def prepare_data(
        self, 
        features: pd.DataFrame, 
        target: pd.Series,
        scale_features: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for model training.
        
        Args:
            features: Feature DataFrame
            target: Target Series
            scale_features: Whether to scale features
        
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Remove any remaining NaN values
        valid_indices = ~(features.isnull().any(axis=1) | target.isnull())
        features_clean = features[valid_indices]
        target_clean = target[valid_indices]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_clean, 
            target_clean, 
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            shuffle=False  # Keep temporal order for time series
        )
        
        # Scale features if requested
        if scale_features:
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Store scaler for later use
            self.scalers['standard'] = scaler
            
            return X_train_scaled, X_test_scaled, y_train.values, y_test.values
        
        return X_train.values, X_test.values, y_train.values, y_test.values
    
    def train_random_forest(
        self, 
        features: pd.DataFrame, 
        target: pd.Series,
        model_name: str = "random_forest"
    ) -> Dict[str, Any]:
        """
        Train a Random Forest regressor.
        
        Args:
            features: Feature DataFrame
            target: Target Series
            model_name: Name for the model
        
        Returns:
            Dictionary with training results
        """
        logger.info(f"Training Random Forest model: {model_name}")
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(features, target)
        
        # Create and train model
        rf = RandomForestRegressor(
            n_estimators=self.config.rf_n_estimators,
            max_depth=self.config.rf_max_depth,
            min_samples_split=self.config.rf_min_samples_split,
            min_samples_leaf=self.config.rf_min_samples_leaf,
            random_state=self.config.random_state,
            n_jobs=-1
        )
        
        rf.fit(X_train, y_train)
        
        # Make predictions
        y_train_pred = rf.predict(X_train)
        y_test_pred = rf.predict(X_test)
        
        # Calculate metrics
        train_metrics = self._calculate_metrics(y_train, y_train_pred)
        test_metrics = self._calculate_metrics(y_test, y_test_pred)
        
        # Store model and results
        self.models[model_name] = rf
        self.model_performance[model_name] = {
            'train': train_metrics,
            'test': test_metrics
        }
        
        # Feature importance
        if hasattr(rf, 'feature_importances_'):
            self.feature_importance[model_name] = dict(
                zip(features.columns, rf.feature_importances_)
            )
        
        logger.info(f"Random Forest training completed. Test R²: {test_metrics['r2']:.4f}")
        
        return {
            'model': rf,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'feature_importance': self.feature_importance.get(model_name, {})
        }
    
    def train_xgboost(
        self, 
        features: pd.DataFrame, 
        target: pd.Series,
        model_name: str = "xgboost"
    ) -> Dict[str, Any]:
        """
        Train an XGBoost regressor.
        
        Args:
            features: Feature DataFrame
            target: Target Series
            model_name: Name for the model
        
        Returns:
            Dictionary with training results
        """
        logger.info(f"Training XGBoost model: {model_name}")
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(features, target)
        
        # Create and train model
        xgb_model = xgb.XGBRegressor(
            n_estimators=self.config.xgb_n_estimators,
            max_depth=self.config.xgb_max_depth,
            learning_rate=self.config.xgb_learning_rate,
            subsample=self.config.xgb_subsample,
            colsample_bytree=self.config.xgb_colsample_bytree,
            random_state=self.config.random_state,
            n_jobs=-1
        )
        
        xgb_model.fit(X_train, y_train)
        
        # Make predictions
        y_train_pred = xgb_model.predict(X_train)
        y_test_pred = xgb_model.predict(X_test)
        
        # Calculate metrics
        train_metrics = self._calculate_metrics(y_train, y_train_pred)
        test_metrics = self._calculate_metrics(y_test, y_test_pred)
        
        # Store model and results
        self.models[model_name] = xgb_model
        self.model_performance[model_name] = {
            'train': train_metrics,
            'test': test_metrics
        }
        
        # Feature importance
        if hasattr(xgb_model, 'feature_importances_'):
            self.feature_importance[model_name] = dict(
                zip(features.columns, xgb_model.feature_importances_)
            )
        
        logger.info(f"XGBoost training completed. Test R²: {test_metrics['r2']:.4f}")
        
        return {
            'model': xgb_model,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'feature_importance': self.feature_importance.get(model_name, {})
        }
    
    def cross_validate_model(
        self, 
        features: pd.DataFrame, 
        target: pd.Series,
        model_type: str = "random_forest"
    ) -> Dict[str, Any]:
        """
        Perform time series cross-validation.
        
        Args:
            features: Feature DataFrame
            target: Target Series
            model_type: Type of model to validate
        
        Returns:
            Dictionary with cross-validation results
        """
        logger.info(f"Performing cross-validation for {model_type}")
        
        # Remove NaN values
        valid_indices = ~(features.isnull().any(axis=1) | target.isnull())
        features_clean = features[valid_indices]
        target_clean = target[valid_indices]
        
        # Time series split
        tscv = TimeSeriesSplit(n_splits=self.config.n_splits)
        
        cv_scores = []
        fold_results = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(features_clean)):
            X_train, X_val = features_clean.iloc[train_idx], features_clean.iloc[val_idx]
            y_train, y_val = target_clean.iloc[train_idx], target_clean.iloc[val_idx]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # Train model
            if model_type == "random_forest":
                model = RandomForestRegressor(
                    n_estimators=self.config.rf_n_estimators,
                    random_state=self.config.random_state,
                    n_jobs=-1
                )
            elif model_type == "xgboost":
                model = xgb.XGBRegressor(
                    n_estimators=self.config.xgb_n_estimators,
                    random_state=self.config.random_state,
                    n_jobs=-1
                )
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_val_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_val, y_pred)
            r2 = r2_score(y_val, y_pred)
            
            cv_scores.append(r2)
            fold_results.append({
                'fold': fold,
                'mse': mse,
                'r2': r2,
                'train_size': len(train_idx),
                'val_size': len(val_idx)
            })
        
        avg_r2 = np.mean(cv_scores)
        std_r2 = np.std(cv_scores)
        
        logger.info(f"Cross-validation completed. Avg R²: {avg_r2:.4f} ± {std_r2:.4f}")
        
        return {
            'avg_r2': avg_r2,
            'std_r2': std_r2,
            'fold_results': fold_results
        }
    
    def predict_returns(
        self, 
        features: pd.DataFrame, 
        model_name: str = "random_forest"
    ) -> np.ndarray:
        """
        Predict returns using trained model.
        
        Args:
            features: Feature DataFrame
            model_name: Name of the model to use
        
        Returns:
            Predicted returns
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Train the model first.")
        
        model = self.models[model_name]
        
        # Scale features if scaler is available
        if 'standard' in self.scalers:
            features_scaled = self.scalers['standard'].transform(features)
            predictions = model.predict(features_scaled)
        else:
            predictions = model.predict(features.values)
        
        self.predictions[model_name] = predictions
        
        return predictions
    
    def get_expected_returns(
        self, 
        features_dict: Dict[str, pd.DataFrame],
        model_name: str = "random_forest"
    ) -> Dict[str, float]:
        """
        Get expected returns for multiple assets.
        
        Args:
            features_dict: Dictionary of features for each asset
            model_name: Name of the model to use
        
        Returns:
            Dictionary of expected returns by ticker
        """
        expected_returns = {}
        
        for ticker, features in features_dict.items():
            try:
                # Use the last row of features (most recent)
                latest_features = features.iloc[-1:].copy()
                
                # Predict return
                predicted_return = self.predict_returns(latest_features, model_name)
                expected_returns[ticker] = float(predicted_return[0])
                
            except Exception as e:
                logger.warning(f"Failed to predict return for {ticker}: {str(e)}")
                expected_returns[ticker] = 0.0
        
        return expected_returns
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
        
        Returns:
            Dictionary of metrics
        """
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred)
        }
    
    def get_best_model(self) -> Tuple[str, Dict[str, Any]]:
        """
        Get the best performing model based on test R².
        
        Returns:
            Tuple of (model_name, performance_metrics)
        """
        if not self.model_performance:
            raise ValueError("No models trained yet")
        
        best_model = max(
            self.model_performance.items(),
            key=lambda x: x[1]['test']['r2']
        )
        
        return best_model
    
    def save_model(self, model_name: str, filepath: str) -> None:
        """
        Save a trained model to disk.
        
        Args:
            model_name: Name of the model to save
            filepath: Path to save the model
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model_data = {
            'model': self.models[model_name],
            'scaler': self.scalers.get('standard'),
            'config': self.config,
            'performance': self.model_performance[model_name]
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model {model_name} saved to {filepath}")
    
    def load_model(self, filepath: str, model_name: str) -> None:
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to the saved model
            model_name: Name to assign to the loaded model
        """
        model_data = joblib.load(filepath)
        
        self.models[model_name] = model_data['model']
        if model_data['scaler'] is not None:
            self.scalers['standard'] = model_data['scaler']
        self.model_performance[model_name] = model_data['performance']
        
        logger.info(f"Model loaded from {filepath} as {model_name}")


if __name__ == "__main__":
    # Example usage
    from data_loader import DataLoader
    from feature_engineering import FeatureEngineer
    
    # Load data and create features
    loader = DataLoader()
    prices = loader.download_stock_data(["AAPL", "MSFT"], period="2y")
    
    engineer = FeatureEngineer()
    features = engineer.create_feature_matrix(prices)
    
    # Get features and target for AAPL
    X, y = engineer.get_feature_importance_data("AAPL")
    
    # Train models
    predictor = ReturnPredictor()
    
    # Train Random Forest
    rf_results = predictor.train_random_forest(X, y, "rf_aapl")
    
    # Train XGBoost
    xgb_results = predictor.train_xgboost(X, y, "xgb_aapl")
    
    # Get best model
    best_model_name, best_performance = predictor.get_best_model()
    print(f"Best model: {best_model_name}")
    print(f"Best R²: {best_performance['test']['r2']:.4f}")
    
    # Cross-validation
    cv_results = predictor.cross_validate_model(X, y, "random_forest")
    print(f"CV R²: {cv_results['avg_r2']:.4f} ± {cv_results['std_r2']:.4f}")
