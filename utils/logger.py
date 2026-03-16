"""
Logger Module

This module provides logging configuration and utilities for the portfolio optimization system.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json

from config import get_config


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with color support for console output.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        # Format the message
        formatted = super().format(record)
        
        return formatted


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    """
    
    def format(self, record):
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName',
                          'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class LoggerManager:
    """
    Manager for application loggers.
    """
    
    def __init__(self):
        """Initialize logger manager."""
        self.loggers = {}
        self.config = get_config()
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger configuration."""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.logging.level))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add console handler
        console_handler = self._create_console_handler()
        root_logger.addHandler(console_handler)
        
        # Add file handler if configured
        if self.config.logging.file_path:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)
    
    def _create_console_handler(self) -> logging.Handler:
        """Create console handler."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, self.config.logging.level))
        
        # Use colored formatter for console
        formatter = ColoredFormatter(self.config.logging.format)
        handler.setFormatter(formatter)
        
        return handler
    
    def _create_file_handler(self) -> logging.Handler:
        """Create rotating file handler."""
        # Create directory if it doesn't exist
        log_file = Path(self.config.logging.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=self.config.logging.file_path,
            maxBytes=self.config.logging.max_file_size,
            backupCount=self.config.logging.backup_count
        )
        handler.setLevel(getattr(logging, self.config.logging.level))
        
        # Use JSON formatter for files
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        
        return handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get logger with specified name.
        
        Args:
            name: Logger name
        
        Returns:
            Logger instance
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def set_level(self, level: str):
        """
        Set logging level for all loggers.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_level = getattr(logging, level.upper())
        
        # Update root logger
        logging.getLogger().setLevel(log_level)
        
        # Update all handlers
        for handler in logging.getLogger().handlers:
            handler.setLevel(log_level)
        
        # Update all registered loggers
        for logger in self.loggers.values():
            logger.setLevel(log_level)


# Global logger manager instance
logger_manager = LoggerManager()


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logger_manager.get_logger(name)


def setup_logging(config_dict: Optional[Dict[str, Any]] = None):
    """
    Setup logging with custom configuration.
    
    Args:
        config_dict: Logging configuration dictionary
    """
    if config_dict:
        # Update configuration
        for key, value in config_dict.items():
            if hasattr(logger_manager.config.logging, key):
                setattr(logger_manager.config.logging, key, value)
        
        # Reconfigure root logger
        logger_manager._setup_root_logger()


class PerformanceLogger:
    """
    Logger for performance metrics and timing.
    """
    
    def __init__(self, logger_name: str = "performance"):
        """Initialize performance logger."""
        self.logger = get_logger(logger_name)
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.start_times[operation] = datetime.now()
        self.logger.debug(f"Started timing: {operation}")
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and log duration."""
        if operation not in self.start_times:
            self.logger.warning(f"No start time found for operation: {operation}")
            return 0.0
        
        start_time = self.start_times[operation]
        duration = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"Operation '{operation}' completed in {duration:.3f} seconds")
        
        del self.start_times[operation]
        return duration
    
    def log_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log a performance metric."""
        message = f"Metric: {metric_name} = {value}"
        if unit:
            message += f" {unit}"
        
        self.logger.info(message)


class AuditLogger:
    """
    Logger for audit trails and security events.
    """
    
    def __init__(self, logger_name: str = "audit"):
        """Initialize audit logger."""
        self.logger = get_logger(logger_name)
    
    def log_request(self, endpoint: str, method: str, user_id: Optional[str] = None, 
                   ip_address: Optional[str] = None):
        """Log API request."""
        self.logger.info(
            f"API Request: {method} {endpoint}",
            extra={
                'event_type': 'api_request',
                'endpoint': endpoint,
                'method': method,
                'user_id': user_id,
                'ip_address': ip_address
            }
        )
    
    def log_optimization(self, tickers: list, method: str, user_id: Optional[str] = None):
        """Log portfolio optimization."""
        self.logger.info(
            f"Portfolio optimization: {method} for {len(tickers)} tickers",
            extra={
                'event_type': 'optimization',
                'tickers': tickers,
                'method': method,
                'user_id': user_id
            }
        )
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context."""
        self.logger.error(
            f"Error occurred: {str(error)}",
            extra={
                'event_type': 'error',
                'error_type': type(error).__name__,
                'context': context or {}
            },
            exc_info=True
        )


def log_function_call(func):
    """
    Decorator to log function calls.
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling function: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {str(e)}")
            raise
    
    return wrapper


def log_performance(operation_name: str):
    """
    Decorator to log function performance.
    
    Args:
        operation_name: Name of the operation for logging
    
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            perf_logger = PerformanceLogger()
            perf_logger.start_timer(operation_name)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                perf_logger.end_timer(operation_name)
        
        return wrapper
    return decorator


# Context manager for timing operations
class Timer:
    """
    Context manager for timing operations.
    """
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        """Initialize timer."""
        self.operation_name = operation_name
        self.logger = logger or get_logger("timing")
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = datetime.now()
        self.logger.debug(f"Started: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log duration."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.logger.info(f"Completed: {self.operation_name} in {duration:.3f} seconds")
        
        return False


if __name__ == "__main__":
    # Test logging configuration
    
    # Get logger
    logger = get_logger(__name__)
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test performance logging
    perf_logger = PerformanceLogger()
    perf_logger.start_timer("test_operation")
    import time
    time.sleep(0.1)
    perf_logger.end_timer("test_operation")
    
    # Test timer context manager
    with Timer("test_context"):
        time.sleep(0.05)
    
    # Test audit logging
    audit_logger = AuditLogger()
    audit_logger.log_request("/optimize", "POST", user_id="test_user")
    audit_logger.log_optimization(["AAPL", "MSFT"], "max_sharpe")
    
    print("Logging test completed")
