"""
FastAPI Server for Portfolio Optimization

This module provides a REST API for portfolio optimization.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Dict, Optional, Any
import logging
import asyncio
from datetime import datetime
import uuid
import json

# Add the src directory to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pipeline import PortfolioOptimizationPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio Optimization API",
    description="AI-powered portfolio optimization using Modern Portfolio Theory",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for running tasks
running_tasks = {}


class OptimizationRequest(BaseModel):
    """Request model for portfolio optimization."""
    tickers: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    optimization_method: str = "max_sharpe"
    risk_free_rate: float = 0.02
    enable_ml_prediction: bool = True
    weight_bounds: tuple = (0.0, 1.0)
    
    @validator('tickers')
    def validate_tickers(cls, v):
        if not v or len(v) < 2:
            raise ValueError("At least 2 tickers are required")
        if len(v) > 50:
            raise ValueError("Maximum 50 tickers allowed")
        return v
    
    @validator('optimization_method')
    def validate_optimization_method(cls, v):
        allowed_methods = ['max_sharpe', 'min_volatility', 'equal_weight']
        if v not in allowed_methods:
            raise ValueError(f"Method must be one of: {allowed_methods}")
        return v
    
    @validator('risk_free_rate')
    def validate_risk_free_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Risk-free rate must be between 0 and 1")
        return v


class TaskResponse(BaseModel):
    """Response model for task status."""
    task_id: str
    status: str
    message: str
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None


class OptimizationResponse(BaseModel):
    """Response model for optimization results."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio Optimization API",
        "version": "1.0.0",
        "endpoints": {
            "optimize": "/optimize",
            "task_status": "/task/{task_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_portfolio(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    Optimize portfolio weights for given tickers.
    
    Args:
        request: Optimization request parameters
        background_tasks: Background task manager
    
    Returns:
        Optimization response with task ID
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        running_tasks[task_id] = {
            "status": "queued",
            "progress": 0.0,
            "message": "Task queued for processing",
            "result": None,
            "error": None
        }
        
        # Start background task
        background_tasks.add_task(
            run_optimization_task,
            task_id,
            request.dict()
        )
        
        logger.info(f"Optimization task started: {task_id}")
        
        return OptimizationResponse(
            success=True,
            message="Optimization task started",
            task_id=task_id
        )
        
    except Exception as e:
        logger.error(f"Failed to start optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """
    Get status of optimization task.
    
    Args:
        task_id: Task ID
    
    Returns:
        Task status response
    """
    if task_id not in running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = running_tasks[task_id]
    
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        message=task["message"],
        progress=task.get("progress"),
        result=task.get("result")
    )


@app.post("/optimize/sync", response_model=OptimizationResponse)
async def optimize_portfolio_sync(request: OptimizationRequest):
    """
    Optimize portfolio synchronously (for testing/small portfolios).
    
    Args:
        request: Optimization request parameters
    
    Returns:
        Optimization results
    """
    try:
        # Validate request size for sync processing
        if len(request.tickers) > 10:
            raise HTTPException(
                status_code=400,
                detail="Synchronous processing limited to 10 tickers. Use /optimize for larger portfolios."
            )
        
        # Create pipeline
        config = {
            'risk_free_rate': request.risk_free_rate,
            'optimization_method': request.optimization_method,
            'enable_ml_prediction': request.enable_ml_prediction,
            'weight_bounds': request.weight_bounds
        }
        
        pipeline = PortfolioOptimizationPipeline(config)
        
        # Run optimization
        results = pipeline.run(
            tickers=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Format response
        formatted_results = format_optimization_results(results)
        
        return OptimizationResponse(
            success=True,
            message="Optimization completed successfully",
            data=formatted_results
        )
        
    except Exception as e:
        logger.error(f"Synchronous optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tickers/validate")
async def validate_tickers(tickers: str):
    """
    Validate if tickers are available.
    
    Args:
        tickers: Comma-separated list of tickers
    
    Returns:
        Validation results
    """
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(",")]
        
        # Basic validation
        invalid_tickers = []
        for ticker in ticker_list:
            if not ticker.isalpha() or len(ticker) < 1 or len(ticker) > 5:
                invalid_tickers.append(ticker)
        
        return {
            "valid": len(invalid_tickers) == 0,
            "tickers": ticker_list,
            "invalid_tickers": invalid_tickers,
            "message": "All tickers valid" if len(invalid_tickers) == 0 else f"Invalid tickers: {invalid_tickers}"
        }
        
    except Exception as e:
        logger.error(f"Ticker validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/methods")
async def get_optimization_methods():
    """
    Get available optimization methods.
    
    Returns:
        Available optimization methods
    """
    methods = {
        "max_sharpe": {
            "name": "Maximum Sharpe Ratio",
            "description": "Optimize portfolio to maximize risk-adjusted returns"
        },
        "min_volatility": {
            "name": "Minimum Volatility",
            "description": "Optimize portfolio to minimize risk"
        },
        "equal_weight": {
            "name": "Equal Weight",
            "description": "Allocate equal weights to all assets"
        }
    }
    
    return {
        "methods": methods,
        "default": "max_sharpe"
    }


async def run_optimization_task(task_id: str, request_data: Dict[str, Any]):
    """
    Run optimization task in background.
    
    Args:
        task_id: Task ID
        request_data: Request parameters
    """
    try:
        # Update task status
        running_tasks[task_id]["status"] = "running"
        running_tasks[task_id]["message"] = "Initializing pipeline"
        running_tasks[task_id]["progress"] = 0.1
        
        # Create pipeline
        config = {
            'risk_free_rate': request_data.get('risk_free_rate', 0.02),
            'optimization_method': request_data.get('optimization_method', 'max_sharpe'),
            'enable_ml_prediction': request_data.get('enable_ml_prediction', True),
            'weight_bounds': request_data.get('weight_bounds', (0.0, 1.0))
        }
        
        pipeline = PortfolioOptimizationPipeline(config)
        
        # Update progress
        running_tasks[task_id]["progress"] = 0.2
        running_tasks[task_id]["message"] = "Downloading data"
        
        # Run optimization
        results = pipeline.run(
            tickers=request_data['tickers'],
            start_date=request_data.get('start_date'),
            end_date=request_data.get('end_date')
        )
        
        # Update progress
        running_tasks[task_id]["progress"] = 0.9
        running_tasks[task_id]["message"] = "Formatting results"
        
        # Format results
        formatted_results = format_optimization_results(results)
        
        # Complete task
        running_tasks[task_id]["status"] = "completed"
        running_tasks[task_id]["progress"] = 1.0
        running_tasks[task_id]["message"] = "Optimization completed successfully"
        running_tasks[task_id]["result"] = formatted_results
        
        logger.info(f"Optimization task completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Optimization task failed: {task_id} - {str(e)}")
        
        # Update task with error
        running_tasks[task_id]["status"] = "failed"
        running_tasks[task_id]["message"] = f"Optimization failed: {str(e)}"
        running_tasks[task_id]["error"] = str(e)


def format_optimization_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format optimization results for API response.
    
    Args:
        results: Raw optimization results
    
    Returns:
        Formatted results
    """
    formatted = {
        "timestamp": results.get("timestamp"),
        "tickers": results.get("tickers"),
        "optimization": {
            "method": "max_sharpe",  # This should come from config
            "success": results["optimization_result"]["success"],
            "message": results["optimization_result"]["message"]
        },
        "portfolio": {
            "weights": results["optimization_result"]["weights"],
            "expected_return": results["optimization_result"]["expected_return"],
            "volatility": results["optimization_result"]["volatility"],
            "sharpe_ratio": results["optimization_result"]["sharpe_ratio"]
        },
        "risk_metrics": {},
        "insights": {},
        "data_summary": results.get("data_summary", {})
    }
    
    # Add risk metrics if available
    if "risk_metrics" in results:
        risk_metrics = results["risk_metrics"]
        formatted["risk_metrics"] = {
            "sharpe_ratio": risk_metrics.get("sharpe_ratio"),
            "sortino_ratio": risk_metrics.get("sortino_ratio"),
            "max_drawdown": risk_metrics.get("drawdown_analysis", {}).get("max_drawdown"),
            "var_95%": risk_metrics.get("var_95%", {}).get("var_5%"),
            "calmar_ratio": risk_metrics.get("calmar_ratio"),
            "omega_ratio": risk_metrics.get("omega_ratio")
        }
    
    # Add insights if available
    if "insights" in results:
        insights = results["insights"]
        formatted["insights"] = {
            "concentration": insights.get("concentration_metrics", {}),
            "monte_carlo": insights.get("monte_carlo_simulation", {})
        }
    
    return formatted


@app.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """
    Delete completed task data.
    
    Args:
        task_id: Task ID
    
    Returns:
        Deletion status
    """
    if task_id not in running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = running_tasks[task_id]
    
    # Only allow deletion of completed tasks
    if task["status"] not in ["completed", "failed"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete running task"
        )
    
    del running_tasks[task_id]
    
    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }


@app.get("/tasks")
async def list_tasks():
    """
    List all tasks.
    
    Returns:
        List of tasks
    """
    tasks = []
    for task_id, task_data in running_tasks.items():
        tasks.append({
            "task_id": task_id,
            "status": task_data["status"],
            "message": task_data["message"],
            "progress": task_data.get("progress")
        })
    
    return {
        "tasks": tasks,
        "total": len(tasks)
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
