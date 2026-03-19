// API Configuration
const API_BASE_URL = process.env.API_BASE_URL || 'https://portfolio-optimization-api.onrender.com';

// Portfolio presets
const PRESETS = {
    tech: ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META'],
    sp500: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'JNJ', 'V'],
    growth: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX', 'ADBE', 'CRM'],
    bluechip: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'JPM', 'JNJ', 'V', 'PG', 'KO']
};

// API Client
class PortfolioAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 60000, // 60 seconds timeout for ML operations
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Request interceptor
        this.client.interceptors.request.use(
            config => {
                console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
                return config;
            },
            error => {
                console.error('API Request Error:', error);
                return Promise.reject(error);
            }
        );

        // Response interceptor
        this.client.interceptors.response.use(
            response => {
                console.log(`API Response: ${response.status} ${response.config.url}`);
                return response;
            },
            error => {
                console.error('API Response Error:', error);
                const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';
                throw new Error(errorMessage);
            }
        );
    }

    // Optimize portfolio
    async optimizePortfolio(tickers, method = 'max_sharpe', options = {}) {
        try {
            const payload = {
                tickers: tickers.map(t => t.toUpperCase().trim()),
                optimization_method: method,
                risk_free_rate: options.riskFreeRate || 0.02,
                enable_ml: options.enableML !== false,
                ...options
            };

            console.log('Optimizing portfolio with payload:', payload);

            const response = await this.client.post('/api/optimize', payload);
            return response.data;
        } catch (error) {
            console.error('Portfolio optimization failed:', error);
            throw error;
        }
    }

    // Get available presets
    getPresets() {
        return PRESETS;
    }

    // Health check
    async healthCheck() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }

    // Get supported tickers (optional)
    async getSupportedTickers() {
        try {
            const response = await this.client.get('/api/tickers');
            return response.data;
        } catch (error) {
            console.error('Failed to get supported tickers:', error);
            return [];
        }
    }
}

// Global API instance
const portfolioAPI = new PortfolioAPI();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PortfolioAPI, portfolioAPI, PRESETS };
}
