import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [tickers, setTickers] = useState('AAPL, MSFT, GOOG, AMZN');
  const [method, setMethod] = useState('max_sharpe');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const optimizePortfolio = async () => {
    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post('http://localhost:8000/optimize', {
        tickers: tickers.split(',').map(t => t.trim().toUpperCase()),
        optimization_method: method,
        enable_ml: true
      });

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to optimize portfolio. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>📊 Portfolio Optimization Dashboard</h1>
          <p>AI-Powered Portfolio Optimization using Modern Portfolio Theory</p>
        </header>

        <main className="main">
          <div className="input-section">
            <div className="form-group">
              <label htmlFor="tickers">Stock Tickers (comma-separated)</label>
              <input
                id="tickers"
                type="text"
                value={tickers}
                onChange={(e) => setTickers(e.target.value)}
                placeholder="AAPL, MSFT, GOOG, AMZN"
                className="input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="method">Optimization Method</label>
              <select
                id="method"
                value={method}
                onChange={(e) => setMethod(e.target.value)}
                className="select"
              >
                <option value="max_sharpe">Maximum Sharpe Ratio</option>
                <option value="min_volatility">Minimum Volatility</option>
                <option value="equal_weight">Equal Weight</option>
              </select>
            </div>

            <button
              onClick={optimizePortfolio}
              disabled={loading}
              className="button"
            >
              {loading ? '🔄 Optimizing...' : '🚀 Optimize Portfolio'}
            </button>
          </div>

          {error && (
            <div className="error">
              <strong>Error:</strong> {error}
            </div>
          )}

          {results && (
            <div className="results">
              <h2>📈 Optimization Results</h2>
              
              <div className="metrics">
                <div className="metric">
                  <span className="metric-label">Expected Return</span>
                  <span className="metric-value">
                    {results.optimization_result?.expected_return 
                      ? `${(results.optimization_result.expected_return * 100).toFixed(2)}%`
                      : 'N/A'
                    }
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Volatility</span>
                  <span className="metric-value">
                    {results.optimization_result?.volatility 
                      ? `${(results.optimization_result.volatility * 100).toFixed(2)}%`
                      : 'N/A'
                    }
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Sharpe Ratio</span>
                  <span className="metric-value">
                    {results.optimization_result?.sharpe_ratio?.toFixed(3) || 'N/A'}
                  </span>
                </div>
              </div>

              <div className="allocation">
                <h3>🎯 Portfolio Allocation</h3>
                {results.optimization_result?.weights && (
                  <div className="weights">
                    {Object.entries(results.optimization_result.weights).map(([ticker, weight]) => (
                      <div key={ticker} className="weight-item">
                        <span className="ticker">{ticker}</span>
                        <span className="weight-percentage">{(weight * 100).toFixed(2)}%</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="risk-metrics">
                <h3>⚠️ Risk Analysis</h3>
                {results.risk_metrics && (
                  <div className="risk-items">
                    <div className="risk-item">
                      <span className="risk-label">Sortino Ratio</span>
                      <span className="risk-value">
                        {results.risk_metrics.sortino_ratio?.toFixed(3) || 'N/A'}
                      </span>
                    </div>
                    <div className="risk-item">
                      <span className="risk-label">Max Drawdown</span>
                      <span className="risk-value">
                        {results.risk_metrics.drawdown_analysis?.max_drawdown 
                          ? `${(results.risk_metrics.drawdown_analysis.max_drawdown * 100).toFixed(2)}%`
                          : 'N/A'
                        }
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div className="raw-data">
                <h3>📋 Raw Response</h3>
                <pre className="json-output">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
