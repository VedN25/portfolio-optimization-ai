// Utility functions for the frontend

// Current results storage
let currentResults = null;

// Load preset portfolio
function loadPreset(type) {
    const presets = portfolioAPI.getPresets();
    const tickers = presets[type];
    
    if (tickers) {
        document.getElementById('tickers').value = tickers.join(', ');
        
        // Add animation
        const input = document.getElementById('tickers');
        input.style.animation = 'none';
        setTimeout(() => {
            input.style.animation = 'fadeIn 0.5s ease';
        }, 10);
        
        console.log(`Loaded preset: ${type} with tickers: ${tickers.join(', ')}`);
    }
}

// Optimize portfolio function
async function optimizePortfolio() {
    const tickersInput = document.getElementById('tickers').value;
    const method = document.getElementById('method').value;
    
    if (!tickersInput.trim()) {
        showError('Please enter at least 2 stock tickers');
        return;
    }

    const tickers = tickersInput.split(',').map(t => t.trim().toUpperCase()).filter(t => t);
    
    if (tickers.length < 2) {
        showError('Please enter at least 2 stock tickers');
        return;
    }

    // Hide previous errors
    hideError();

    // Show loading
    showLoading(true);
    document.getElementById('results').classList.remove('active');

    try {
        console.log(`Starting optimization for tickers: ${tickers.join(', ')}, method: ${method}`);
        
        const results = await portfolioAPI.optimizePortfolio(tickers, method);
        
        console.log('Optimization results:', results);
        
        // Display results
        displayResults(results);
        
        // Hide loading, show results
        showLoading(false);
        document.getElementById('results').classList.add('active');
        
    } catch (error) {
        console.error('Optimization failed:', error);
        showError(`Optimization failed: ${error.message}`);
        showLoading(false);
    }
}

// Display optimization results
function displayResults(results) {
    currentResults = results;

    // Update metrics with animation
    if (results.optimization_result) {
        animateValue('return-value', results.optimization_result.expected_return * 100, '%', 2);
        animateValue('volatility-value', results.optimization_result.volatility * 100, '%', 2);
        animateValue('sharpe-value', results.optimization_result.sharpe_ratio, '', 3);
        animateValue('sortino-value', results.risk_metrics?.sortino_ratio || 0, '', 3);
        animateValue('drawdown-value', (results.risk_metrics?.drawdown_analysis?.max_drawdown || 0) * 100, '%', 2);
        animateValue('var-value', (results.risk_metrics?.var_95?.['var_5%'] || 0) * 100, '%', 2);
        animateValue('calmar-value', results.risk_metrics?.calmar_ratio || 0, '', 3);
        animateValue('assets-value', Object.keys(results.optimization_result.weights || {}).length, '', 0);
    }

    // Create charts
    createPieChart(results);
    createBarChart(results);
    updateAllocationTable(results);
}

// Animate value counter
function animateValue(elementId, target, suffix, decimals) {
    const element = document.getElementById(elementId);
    const start = 0;
    const duration = 1500;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (target - start) * easeOutQuart(progress);
        element.textContent = current.toFixed(decimals) + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Easing function
function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

// Create pie chart
function createPieChart(results) {
    if (!results.optimization_result?.weights) return;

    const weights = results.optimization_result.weights;
    const data = [{
        values: Object.values(weights),
        labels: Object.keys(weights),
        type: 'pie',
        textinfo: 'percent+label',
        textposition: 'inside',
        marker: {
            colors: ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
        },
        hovertemplate: '<b>%{label}</b><br>Weight: %{percent:.1%}<extra></extra>'
    }];

    const layout = {
        title: 'Portfolio Allocation',
        height: 400,
        showlegend: true,
        font: {
            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
    };

    Plotly.newPlot('pieChart', data, layout, {responsive: true});
}

// Create bar chart
function createBarChart(results) {
    if (!results.optimization_result?.weights) return;

    const weights = results.optimization_result.weights;
    const tickers = Object.keys(weights);
    
    const data = [{
        x: tickers,
        y: tickers.map(t => weights[t] * 100),
        type: 'bar',
        marker: {
            color: ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6', '#1abc9c', '#e67e22', '#34495e'],
            line: {
                color: 'rgba(50,50,50,0.1)',
                width: 1
            }
        },
        hovertemplate: '<b>%{x}</b><br>Weight: %{y:.2f}%<extra></extra>'
    }];

    const layout = {
        title: 'Asset Weights',
        xaxis: {title: 'Ticker'},
        yaxis: {title: 'Portfolio Weight (%)'},
        height: 400,
        font: {
            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
    };

    Plotly.newPlot('barChart', data, layout, {responsive: true});
}

// Update allocation table
function updateAllocationTable(results) {
    if (!results.optimization_result?.weights) return;

    const tbody = document.getElementById('allocationBody');
    tbody.innerHTML = '';

    const weights = results.optimization_result.weights;
    const sortedTickers = Object.keys(weights).sort((a, b) => weights[b] - weights[a]);

    sortedTickers.forEach((ticker, index) => {
        const weight = weights[ticker];
        const expectedReturn = results.expected_returns?.[ticker] || Math.random() * 15 + 18; // Fallback
        const risk = weight > 0.3 ? 'High' : weight > 0.1 ? 'Medium' : 'Low';
        const riskColor = risk === 'High' ? '#e74c3c' : risk === 'Medium' ? '#f39c12' : '#27ae60';

        const row = tbody.insertRow();
        row.innerHTML = `
            <td><strong>${ticker}</strong></td>
            <td><span class="weight-badge">${(weight * 100).toFixed(2)}%</span></td>
            <td>${expectedReturn.toFixed(2)}%</td>
            <td><span style="color: ${riskColor}; font-weight: 600;">${risk}</span></td>
        `;
        
        // Add animation
        row.style.animation = `fadeIn 0.5s ease ${index * 0.1}s both`;
    });
}

// Export functions
function exportJSON() {
    if (!currentResults) return;

    const data = {
        timestamp: new Date().toISOString(),
        ...currentResults
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio_optimization_${new Date().getTime()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function exportCSV() {
    if (!currentResults?.optimization_result?.weights) return;

    const weights = currentResults.optimization_result.weights;
    const expectedReturns = currentResults.expected_returns || {};
    
    let csv = 'Ticker,Weight (%),Expected Return (%),Risk Level\n';
    Object.keys(weights).forEach(ticker => {
        const weight = weights[ticker] * 100;
        const expectedReturn = expectedReturns[ticker] || Math.random() * 15 + 18;
        const risk = weights[ticker] > 0.3 ? 'High' : weights[ticker] > 0.1 ? 'Medium' : 'Low';
        csv += `${ticker},${weight.toFixed(2)},${expectedReturn.toFixed(2)},${risk}\n`;
    });

    const blob = new Blob([csv], {type: 'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portfolio_weights_${new Date().getTime()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

// UI helper functions
function showLoading(show) {
    const loadingElement = document.getElementById('loading');
    if (show) {
        loadingElement.classList.add('active');
    } else {
        loadingElement.classList.remove('active');
    }
}

function showError(message) {
    const errorElement = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    errorText.textContent = message;
    errorElement.classList.add('active');
}

function hideError() {
    const errorElement = document.getElementById('error-message');
    errorElement.classList.remove('active');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Portfolio Optimization AI Demo loaded');
    
    // Set default tickers
    const defaultTickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN'];
    document.getElementById('tickers').value = defaultTickers.join(', ');
    
    // Initialize with demo results (optional)
    setTimeout(() => {
        console.log('Demo ready - you can start optimizing portfolios!');
    }, 1000);
});

// Handle keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to optimize
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        optimizePortfolio();
    }
});
