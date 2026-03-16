# Portfolio Optimization AI

🚀 **AI-Powered Portfolio Optimization using Modern Portfolio Theory & Machine Learning**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📊 Overview

Portfolio Optimization AI is an end-to-end machine learning system that predicts asset returns and performs portfolio optimization using Modern Portfolio Theory (MPT). The system combines advanced ML models with quantitative finance techniques to generate optimal portfolio allocations.

## ✨ Key Features

- **🤖 AI-Powered Predictions**: Uses RandomForest and XGBoost to predict expected returns
- **📈 Modern Portfolio Theory**: Implements Markowitz mean-variance optimization
- **🎯 Multiple Optimization Strategies**: Max Sharpe ratio, minimum volatility, equal weight
- **⚠️ Comprehensive Risk Analysis**: VaR, maximum drawdown, Sortino ratio, and more
- **🌐 REST API**: FastAPI service for programmatic access
- **📊 Interactive Dashboard**: Streamlit-based visualization interface
- **🐳 Docker Support**: Containerized deployment for easy scaling
- **📦 Feature Engineering**: 20+ technical indicators (RSI, MACD, Bollinger Bands, momentum)

## 🏗️ Architecture

```
portfolio-optimization-ai/
├── src/                    # Core ML modules
│   ├── data_loader.py      # Stock data ingestion
│   ├── feature_engineering.py # Technical indicators
│   ├── return_predictor.py # ML prediction models
│   ├── portfolio_optimizer.py # MPT optimization
│   ├── risk_metrics.py     # Risk analysis
│   └── pipeline.py         # End-to-end workflow
├── api/                    # FastAPI service
│   └── server.py          # REST API endpoints
├── dashboard/              # Streamlit dashboard
│   └── app.py             # Interactive web interface
├── utils/                  # Utilities
│   ├── config.py          # Configuration management
│   └── logger.py          # Logging system
├── deployment/             # Docker files
│   ├── Dockerfile
│   └── run.sh
├── tests/                  # Test suite
└── notebooks/              # Jupyter notebooks
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/portfolio-optimization-ai.git
cd portfolio-optimization-ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the API server**
```bash
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

4. **Launch the dashboard**
```bash
streamlit run dashboard/app.py --server.port 8501
```

### Docker Deployment

```bash
# Build and run with Docker
cd deployment
./run.sh
```

## 📖 Usage Examples

### API Usage

```python
import requests

# Optimize portfolio
response = requests.post(
    "http://localhost:8000/optimize/sync",
    json={
        "tickers": ["AAPL", "MSFT", "GOOG", "AMZN"],
        "optimization_method": "max_sharpe",
        "risk_free_rate": 0.02,
        "enable_ml_prediction": True
    }
)

result = response.json()
print(f"Expected Return: {result['data']['portfolio']['expected_return']:.2%}")
print(f"Volatility: {result['data']['portfolio']['volatility']:.2%}")
print(f"Sharpe Ratio: {result['data']['portfolio']['sharpe_ratio']:.3f}")
```

### Python SDK Usage

```python
from src.pipeline import PortfolioOptimizationPipeline

# Initialize pipeline
pipeline = PortfolioOptimizationPipeline()

# Run optimization
results = pipeline.run(
    tickers=["AAPL", "MSFT", "GOOG", "AMZN"],
    optimization_method="max_sharpe"
)

# Access results
print(f"Optimal weights: {results['optimization_result']['weights']}")
print(f"Expected return: {results['optimization_result']['expected_return']:.2%}")
```

## 🎯 Optimization Methods

### 1. Maximum Sharpe Ratio
Maximizes risk-adjusted returns:
```
max: (E[R] - r_f) / σ
```

### 2. Minimum Volatility
Minimizes portfolio risk:
```
min: σ² = w^T Σ w
```

### 3. Equal Weight
Simple equal allocation across all assets.

## 📊 Risk Metrics

The system calculates comprehensive risk metrics:

- **Sharpe Ratio**: Risk-adjusted performance measure
- **Sortino Ratio**: Downside risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Value at Risk (VaR)**: Potential loss at confidence levels
- **Expected Shortfall**: Average loss beyond VaR
- **Calmar Ratio**: Return to maximum drawdown ratio
- **Omega Ratio**: Probability-weighted ratio of gains to losses

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Data Configuration
DATA_PERIOD=5y
CACHE_DIR=data/cache

# Model Configuration
RF_N_ESTIMATORS=100
XGB_N_ESTIMATORS=100

# Optimization Configuration
RISK_FREE_RATE=0.02
OPTIMIZATION_METHOD=max_sharpe

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/portfolio_optimization.log
```

### Configuration File

Create `config.json`:

```json
{
  "optimization": {
    "risk_free_rate": 0.02,
    "optimization_method": "max_sharpe",
    "enable_ml_prediction": true
  },
  "model": {
    "rf_n_estimators": 100,
    "xgb_n_estimators": 100,
    "random_state": 42
  },
  "data": {
    "default_period": "5y",
    "min_data_points": 252
  }
}
```

## 📈 Example Output

```json
{
  "optimization_result": {
    "weights": {
      "AAPL": 0.25,
      "MSFT": 0.30,
      "GOOG": 0.20,
      "AMZN": 0.25
    },
    "expected_return": 0.18,
    "volatility": 0.12,
    "sharpe_ratio": 1.5
  },
  "risk_metrics": {
    "sharpe_ratio": 1.5,
    "sortino_ratio": 2.1,
    "max_drawdown": -0.15,
    "var_95%": -0.02,
    "calmar_ratio": 1.2
  }
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_optimizer.py
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /optimize` - Async portfolio optimization
- `POST /optimize/sync` - Synchronous optimization
- `GET /task/{task_id}` - Task status
- `GET /health` - Health check
- `GET /methods` - Available optimization methods

## 🎨 Dashboard Features

The Streamlit dashboard provides:

- **Portfolio Input**: Manual ticker entry or predefined portfolios
- **Parameter Configuration**: Optimization method, risk-free rate, constraints
- **Real-time Visualization**: Portfolio allocation charts, risk metrics
- **Export Options**: Download results as JSON/CSV
- **Performance Monitoring**: Sharpe ratio, drawdown, VaR analysis

## 🔬 Technical Details

### Machine Learning Models

1. **RandomForestRegressor**
   - Ensemble decision trees
   - Handles non-linear relationships
   - Feature importance analysis

2. **XGBoostRegressor**
   - Gradient boosting framework
   - High predictive accuracy
   - Regularization to prevent overfitting

### Feature Engineering

- **Returns**: Simple and log returns
- **Volatility**: Rolling standard deviation
- **Moving Averages**: 10, 20, 50-day SMAs
- **RSI**: Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Price volatility bands
- **Momentum**: Price momentum indicators

### Optimization Algorithm

Uses `scipy.optimize.minimize` with SLSQP method:
- Constraints: weights sum to 1, weights ≥ 0
- Bounds: configurable weight limits per asset
- Objective: maximize Sharpe ratio or minimize volatility

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t portfolio-ai .
```

### Run Container

```bash
docker run -d \
  --name portfolio-ai \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  portfolio-ai
```

### Docker Compose

```yaml
version: '3.8'
services:
  portfolio-ai:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=INFO
      - RISK_FREE_RATE=0.02
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/

# Run type checking
mypy src/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **yfinance** for financial data access
- **scikit-learn** for machine learning tools
- **scipy** for optimization algorithms
- **FastAPI** for the web framework
- **Streamlit** for the dashboard interface

## 📞 Support

- 📧 Email: support@portfolio-optimization-ai.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/portfolio-optimization-ai/issues)
- 📖 Documentation: [Wiki](https://github.com/your-username/portfolio-optimization-ai/wiki)

## 🗺️ Roadmap

- [ ] **Enhanced ML Models**: LSTM neural networks for time series
- [ ] **Multi-Asset Classes**: Bonds, commodities, cryptocurrencies
- [ ] **Backtesting Engine**: Historical performance analysis
- [ ] **Real-time Data**: Live market data integration
- [ ] **Portfolio Rebalancing**: Automated rebalancing strategies
- [ ] **Mobile App**: React Native mobile application
- [ ] **Cloud Deployment**: AWS/GCP deployment templates

---

**⭐ Star this repository if it helped you!**

Made with ❤️ using Python, FastAPI, and Streamlit
