/**
 * Updates the stock chart on the stock.html page.
 * Fetches data from the /api/stocks/stock/{symbol}/data endpoint.
 * @param {string} symbol - The stock symbol.
 */
async function updateStockChart(symbol) {
    const chartContainer = document.getElementById('stockChartContainer');
    const periodSelect = document.getElementById('periodSelect');
    const selectedPeriod = periodSelect ? periodSelect.value : '1y'; // Default to 1y if not found

    if (!chartContainer) {
        console.warn("stockChartContainer not found. Chart will not be rendered.");
        return;
    }

    chartContainer.innerHTML = `<p>Loading chart data for ${symbol} (${selectedPeriod})...</p>`;

    try {
        // Use APP_CONFIG.apiBaseUrl defined in base.html for API endpoint construction
        const apiUrl = `${APP_CONFIG.apiBaseUrl}/stocks/stock/${symbol}/data?period=${selectedPeriod}`;
        console.log("Fetching chart data from:", apiUrl);
        const response = await fetch(apiUrl);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Error fetching chart data: ${response.status}`);
        }

        const data = await response.json(); // Expects data in {index: [...], columns: [...], data: [[...], ...]} format

        if (!data || !data.index || data.index.length === 0) {
            chartContainer.innerHTML = `<p>No chart data available for ${symbol} for the selected period.</p>`;
            return;
        }

        // Find column indices for OHLC data (case-insensitive matching for flexibility)
        const findColIndex = (name) => data.columns.findIndex(col => col.toLowerCase() === name.toLowerCase());
        
        const dateIndex = data.index;
        const openIndex = findColIndex('Open');
        const highIndex = findColIndex('High');
        const lowIndex = findColIndex('Low');
        const closeIndex = findColIndex('Close');
        const volumeIndex = findColIndex('Volume'); // Optional

        if ([openIndex, highIndex, lowIndex, closeIndex].some(idx => idx === -1)) {
            console.error("Missing one or more OHLC columns in the data:", data.columns);
            chartContainer.innerHTML = "<p>Chart data is missing required OHLC columns. Cannot render chart.</p>";
            return;
        }

        const traceCandlestick = {
            x: dateIndex,
            open: data.data.map(row => row[openIndex]),
            high: data.data.map(row => row[highIndex]),
            low: data.data.map(row => row[lowIndex]),
            close: data.data.map(row => row[closeIndex]),
            type: 'candlestick',
            name: symbol,
            increasing: {line: {color: '#26a69a'}, fillcolor: '#26a69a'}, // Tealish green
            decreasing: {line: {color: '#ef5350'}, fillcolor: '#ef5350'}  // Reddish
        };

        const layout = {
            title: `${symbol} Stock Price (${selectedPeriod.toUpperCase()})`,
            xaxis: {
                title: 'Date',
                type: 'date',
                rangeslider: { visible: false } // Can be enabled if desired
            },
            yaxis: {
                title: 'Price (USD)',
                autorange: true
            },
            margin: { t: 50, b: 50, l: 50, r: 20 },
            paper_bgcolor: '#f4f7f6',
            plot_bgcolor: '#ffffff',
            font: {
                family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
            }
        };
        
        const plotData = [traceCandlestick];

        // Add Volume bar chart if volume data is available
        if (volumeIndex !== -1) {
            const traceVolume = {
                x: dateIndex,
                y: data.data.map(row => row[volumeIndex]),
                type: 'bar',
                name: 'Volume',
                yaxis: 'y2', // Plot on a secondary y-axis
                marker: {color: 'rgba(100, 100, 100, 0.3)'}
            };
            plotData.push(traceVolume);
            layout.yaxis2 = {
                title: 'Volume',
                overlaying: 'y',
                side: 'right',
                showgrid: false,
                autorange: true
            };
            // Adjust layout to accommodate two y-axes if volume is present
            layout.yaxis.domain = [0.25, 1]; // Main price chart takes top 75%
            layout.yaxis2.domain = [0, 0.2]; // Volume chart takes bottom 20%
        }
        
        Plotly.newPlot(chartContainer, plotData, layout, {responsive: true});
        console.log(`Chart for ${symbol} (${selectedPeriod}) rendered successfully.`);

    } catch (error) {
        console.error(`Error rendering chart for ${symbol}:`, error);
        chartContainer.innerHTML = `<p class="error-message">Failed to load chart data for ${symbol}: ${error.message}</p>`;
    }
}

// Example of how you might call this from other parts of your JS or HTML:
// document.addEventListener('DOMContentLoaded', function() {
//     const currentSymbolElement = document.getElementById('currentStockSymbol'); // Assuming you have such an element
//     if (currentSymbolElement) {
//         updateStockChart(currentSymbolElement.textContent);
//     }
// });

console.log("charts.js loaded and ready."); 