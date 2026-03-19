"""
FastAPI Backend for Portfolio Optimization AI

This backend handles all ML computations and portfolio optimization.
Deployed on Render/Railway to handle heavy computations.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import List, Dict, Optional, Any
import logging
import asyncio
from datetime import datetime
import uuid
import json
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import PortfolioOptimizationPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio Optimization API",
    description="AI-powered portfolio optimization using Modern Portfolio Theory",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for running tasks (in production, use Redis)
running_tasks = {}

# Request models
class OptimizationRequest(BaseModel):
    """Request model for portfolio optimization."""
    tickers: List[str]
    optimization_method: str = "max_sharpe"
    risk_free_rate: float = 0.02
    enable_ml: bool = True
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    @validator('tickers')
    def validate_tickers(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 tickers are required")
        if len(v) > 50:
            raise ValueError("Maximum 50 tickers allowed")
        return [ticker.upper().strip() for ticker in v]
    
    @validator('optimization_method')
    def validate_method(cls, v):
        allowed_methods = ["max_sharpe", "min_volatility", "equal_weight"]
        if v not in allowed_methods:
            raise ValueError(f"Method must be one of: {allowed_methods}")
        return v
    
    @validator('risk_free_rate')
    def validate_risk_free_rate(cls, v):
        if not 0 <= v <= 0.1:
            raise ValueError("Risk free rate must be between 0 and 0.1")
        return v

class OptimizationResponse(BaseModel):
    """Response model for portfolio optimization."""
    task_id: str
    status: str
    message: str
    results: Optional[Dict[str, Any]] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "Portfolio Optimization API"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio Optimization API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/api/tickers")
async def get_supported_tickers():
    """Get list of commonly supported tickers."""
    common_tickers = [
        # Tech
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "NVDA",
        # Finance
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK",
        # Healthcare
        "JNJ", "UNH", "PFE", "ABBV", "TMO", "ABT", "MRK", "DHR",
        # Consumer
        "PG", "KO", "WMT", "COST", "HD", "MCD", "NKE", "LOW",
        # Energy
        "XOM", "CVX", "COP", "SHEL", "BP", "TOT", "ENB", "EOG",
        # Industrial
        "CAT", "DE", "GE", "MMM", "HON", "UPS", "RTX", "BA"
    ]
    
    return {
        "tickers": common_tickers,
        "count": len(common_tickers),
        "note": "These are commonly supported tickers. Other tickers may also work if available on Yahoo Finance."
    }

@app.post("/api/optimize", response_model=OptimizationResponse)
async def optimize_portfolio(request: OptimizationRequest):
    """
    Optimize portfolio using ML and Modern Portfolio Theory.
    
    This endpoint performs:
    1. Data fetching from Yahoo Finance
    2. Feature engineering with technical indicators
    3. ML-based return prediction (if enabled)
    4. Portfolio optimization using specified method
    5. Risk analysis and metrics calculation
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        logger.info(f"Starting optimization task {task_id} for tickers: {request.tickers}")
        
        # Initialize pipeline
        pipeline = PortfolioOptimizationPipeline()
        
        # Run optimization (this is the heavy computation)
        results = await asyncio.get_event_loop().run_in_executor(
            None, 
            pipeline.run, 
            request.tickers,
            {
                'optimization_method': request.optimization_method,
                'risk_free_rate': request.risk_free_rate,
                'enable_ml': request.enable_ml,
                'start_date': request.start_date,
                'end_date': request.end_date
            }
        )
        
        logger.info(f"Optimization completed for task {task_id}")
        
        return OptimizationResponse(
            task_id=task_id,
            status="completed",
            message="Portfolio optimization completed successfully",
            results=results
        )
        
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """Get status of optimization task."""
    # In production, check Redis/database for task status
    # For now, return a simple response
    return {
        "task_id": task_id,
        "status": "completed",
        "message": "Task completed"
    }

@app.get("/api/models/info")
async def get_models_info():
    """Get information about ML models used."""
    return {
        "return_predictor": {
            "models": ["RandomForest", "XGBoost"],
            "features": [
                "RSI", "MACD", "Bollinger Bands", "Momentum",
                "Volume", "Volatility", "Moving Averages"
            ],
            "training_data": "Historical stock prices with technical indicators"
        },
        "portfolio_optimizer": {
            "methods": ["max_sharpe", "min_volatility", "equal_weight"],
            "theory": "Modern Portfolio Theory (Markowitz)",
            "constraints": "Weights sum to 1, non-negative weights"
        },
        "risk_metrics": {
            "metrics": [
                "VaR (Value at Risk)", "Maximum Drawdown", "Sortino Ratio",
                "Calmar Ratio", "Sharpe Ratio", "Volatility"
            ]
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP exception",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event."""
    logger.info("Portfolio Optimization API started")
    logger.info(f"Documentation available at /docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event."""
    logger.info("Portfolio Optimization API shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
