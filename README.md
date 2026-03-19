# Portfolio Optimization AI

🚀 **AI-Powered Portfolio Optimization using Modern Portfolio Theory & Machine Learning**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![Vercel](https://img.shields.io/badge/Vercel-000000-black.svg)
![Render](https://img.shields.io/badge/Render-46E3B7.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📊 Overview

Portfolio Optimization AI is an end-to-end machine learning system that predicts asset returns and performs portfolio optimization using Modern Portfolio Theory (MPT). The system combines advanced ML models with quantitative finance techniques to generate optimal portfolio allocations.

**🎯 Try the Live Demo:** [Portfolio Optimization AI Demo](https://portfolio-optimization-ai-frontend.vercel.app/)

## ✨ Key Features

- **🤖 AI-Powered Predictions**: Uses RandomForest and XGBoost to predict expected returns
- **📈 Modern Portfolio Theory**: Implements Markowitz mean-variance optimization
- **🎯 Multiple Optimization Strategies**: Max Sharpe ratio, minimum volatility, equal weight
- **⚠️ Comprehensive Risk Analysis**: VaR, maximum drawdown, Sortino ratio, and more
- **🌐 REST API**: FastAPI service for programmatic access
- **📊 Interactive Dashboard**: Modern web interface with real-time optimization
- **� Production Ready**: Separated frontend/backend architecture
- **📦 Feature Engineering**: 20+ technical indicators (RSI, MACD, Bollinger Bands, momentum)

## 🏗️ Architecture

```
portfolio-optimization-ai/
├── frontend/               # Vercel deployment (< 50KB)
│   ├── public/
│   │   ├── index.html     # Interactive demo
│   │   └── src/
│   │       ├── api.js     # API client
│   │       └── utils.js   # UI utilities
│   └── package.json       # Minimal dependencies
├── backend/                # Render/Railway deployment (~200MB)
│   ├── app.py            # FastAPI server
│   ├── requirements.txt  # ML dependencies
│   └── src/              # All ML modules
│       ├── data_loader.py
│       ├── feature_engineering.py
│       ├── return_predictor.py
│       ├── portfolio_optimizer.py
│       ├── risk_metrics.py
│       └── pipeline.py
└── deployment guides
```

## 🚀 Production Deployment

### Frontend (Vercel)
- **URL**: https://portfolio-optimization-ai-frontend.vercel.app
- **Size**: ~50KB (99.99% reduction from original)
- **Tech**: Static HTML + JavaScript + Axios
- **Features**: Interactive UI, real-time API calls, charts

### Backend (Render/Railway)
- **URL**: https://portfolio-optimization-api.onrender.com
- **Size**: ~200MB (ML dependencies only)
- **Tech**: FastAPI + Python ML stack
- **Features**: ML models, portfolio optimization, risk analysis

## 🚀 Quick Start

### 🎯 Try the Live Demo
**Interactive Demo**: https://portfolio-optimization-ai-frontend.vercel.app/

1. Enter stock tickers (e.g., AAPL, MSFT, GOOG, AMZN)
2. Choose optimization method
3. Click "Optimize Portfolio"
4. View results with interactive charts

### 📊 API Usage
```bash
# Health check
curl https://portfolio-optimization-api.onrender.com/health

# Optimize portfolio
curl -X POST "https://portfolio-optimization-api.onrender.com/api/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOG", "AMZN"],
    "optimization_method": "max_sharpe",
    "enable_ml": true
  }'
```

### 📱 Local Development

#### Frontend Only
```bash
cd frontend
python -m http.server 3000
# Visit http://localhost:3000
```

#### Full Stack
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
python -m http.server 3000
```

## 📊 Results Example

### Portfolio Optimization Results
```
📈 Performance Metrics:
• Expected Annual Return: 24.33%
• Annual Volatility: 27.42%
• Sharpe Ratio: 0.814
• Sortino Ratio: 1.196

🎯 Optimal Allocation:
• GOOG: 74.80%
• AAPL: 25.20%
• AMZN: 0.00%
• MSFT: 0.00%
```

## 🛠️ Deployment

### 🚀 Production Deployment

#### Frontend (Vercel)
1. Go to [vercel.com](https://vercel.com)
2. Import `frontend` folder from GitHub
3. Deploy (instant, < 30 seconds)

#### Backend (Render)
1. Go to [render.com](https://render.com)
2. Import `backend` folder from GitHub
3. Deploy (3-5 minutes)

📖 **Detailed Guide**: See [README_DEPLOYMENT.md](README_DEPLOYMENT.md)

### 🐳 Docker Deployment
```bash
# Build and run
docker-compose up -d

# Access services
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 📈 Build Size Optimization

| Component | Before | After | Reduction |
|-----------|--------|-------|-----------|
| **Frontend** | 1216MB | 50KB | **99.99%** |
| **Backend** | N/A | 200MB | New |
| **Total** | **1216MB** | **250MB** | **79%** |

📖 **Analysis**: See [DEPENDENCIES_ANALYSIS.md](DEPENDENCIES_ANALYSIS.md)

## 🎯 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /api/tickers` - Supported tickers list
- `POST /api/optimize` - Portfolio optimization
- `GET /api/models/info` - ML models information
- `GET /docs` - API documentation

### Request Example
```json
{
  "tickers": ["AAPL", "MSFT", "GOOG", "AMZN"],
  "optimization_method": "max_sharpe",
  "risk_free_rate": 0.02,
  "enable_ml": true
}
```

### Response Example
```json
{
  "task_id": "uuid",
  "status": "completed",
  "results": {
    "optimization_result": {
      "weights": {"AAPL": 0.252, "GOOG": 0.748},
      "expected_return": 0.2433,
      "volatility": 0.2742,
      "sharpe_ratio": 0.814
    },
    "risk_metrics": {
      "sortino_ratio": 1.196,
      "max_drawdown": -0.3874,
      "var_95%": {"var_5%": -0.0259}
    }
  }
}
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Coverage
- Unit tests for all ML models
- Integration tests for API endpoints
- Portfolio optimization validation
- Risk metrics calculation tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Modern Portfolio Theory**: Harry Markowitz
- **Yahoo Finance API**: Financial data source
- **scikit-learn**: Machine learning framework
- **FastAPI**: Web framework for APIs
- **Vercel**: Frontend hosting platform
- **Render**: Backend hosting platform

## 📞 Contact

- **GitHub**: [@VedN25](https://github.com/VedN25)
- **LinkedIn**: [Ved Nawale](https://www.linkedin.com/in/vednawale)
- **Email**: vednawale1@gmail.com

---

## 🎯 LinkedIn Showcase

**🚀 Portfolio Optimization AI - Live Demo**

📊 **Results**: 24.33% expected return, 0.814 Sharpe ratio  
🎯 **Tech**: ML + Modern Portfolio Theory  
🌐 **Demo**: https://portfolio-optimization-ai-frontend.vercel.app/  
📁 **Code**: https://github.com/VedN25/portfolio-optimization-ai  

#MachineLearning #PortfolioOptimization #FinTech #AI #QuantitativeFinance

Made with ❤️ using Python, FastAPI, and Streamlit
