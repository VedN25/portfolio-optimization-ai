from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import random

app = FastAPI(title="Portfolio Optimization API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptimizationRequest(BaseModel):
    tickers: List[str]
    optimization_method: str = "max_sharpe"
    enable_ml: bool = True

def generate_sample_results(tickers: List[str], method: str) -> Dict[str, Any]:
    """Generate sample portfolio optimization results"""
    
    # Generate random weights that sum to 1
    weights = []
    remaining = 1.0
    for i in range(len(tickers) - 1):
        weight = random.uniform(0, remaining * 0.8)
        weights.append(weight)
        remaining -= weight
    weights.append(remaining)  # Last ticker gets remaining weight
    
    weights_dict = {ticker: round(weight, 4) for ticker, weight in zip(tickers, weights)}
    
    # Generate realistic metrics based on method
    if method == "max_sharpe":
        expected_return = random.uniform(0.18, 0.28)
        volatility = random.uniform(0.22, 0.32)
    elif method == "min_volatility":
        expected_return = random.uniform(0.12, 0.20)
        volatility = random.uniform(0.15, 0.22)
    else:  # equal_weight
        expected_return = random.uniform(0.15, 0.22)
        volatility = random.uniform(0.20, 0.28)
    
    sharpe_ratio = round(expected_return / volatility, 3)
    sortino_ratio = round(sharpe_ratio * random.uniform(1.2, 1.5), 3)
    max_drawdown = round(-random.uniform(0.25, 0.45), 3)
    
    return {
        "optimization_result": {
            "weights": weights_dict,
            "expected_return": round(expected_return, 4),
            "volatility": round(volatility, 4),
            "sharpe_ratio": sharpe_ratio
        },
        "risk_metrics": {
            "sortino_ratio": sortino_ratio,
            "drawdown_analysis": {
                "max_drawdown": max_drawdown
            },
            "var_95%": {
                "var_5%": round(-random.uniform(0.02, 0.04), 4)
            },
            "calmar_ratio": round(expected_return / abs(max_drawdown), 3)
        },
        "expected_returns": {ticker: round(random.uniform(0.15, 0.30), 4) for ticker in tickers}
    }

@app.get("/")
async def root():
    return {"message": "Portfolio Optimization API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "portfolio-optimization-api"}

@app.post("/optimize")
async def optimize_portfolio(request: OptimizationRequest):
    """
    Optimize portfolio based on provided tickers and method
    """
    try:
        # Validate input
        if len(request.tickers) < 2:
            raise HTTPException(status_code=400, detail="At least 2 tickers are required")
        
        if len(request.tickers) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 tickers allowed")
        
        # Generate sample results (in production, this would run actual ML models)
        results = generate_sample_results(request.tickers, request.optimization_method)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.get("/methods")
async def get_optimization_methods():
    """Get available optimization methods"""
    return {
        "methods": [
            {
                "name": "max_sharpe",
                "description": "Maximize risk-adjusted returns"
            },
            {
                "name": "min_volatility", 
                "description": "Minimize portfolio volatility"
            },
            {
                "name": "equal_weight",
                "description": "Equal allocation across all assets"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
