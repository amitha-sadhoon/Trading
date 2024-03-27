anychart.onDocumentReady(function () {

    var button1M = document.getElementById("1m");
    var button3M = document.getElementById("3m");
    var button6M = document.getElementById("6m");
    var button1Y = document.getElementById("1y");
    var button2Y = document.getElementById("2y");
    var button5Y = document.getElementById("5y");
    var graph = document.getElementById("stock-graph");

    var stockSymbol = document.getElementById("stock-symbol").innerHTML;
    console.log(stockSymbol);

    // Show 1y history by default
    window.addEventListener("load", function() {
        // graph.innerHTML = "";
        // getStockChart(stockSymbol, '1y', function(sixMonthData, chartTitle) {
        //     drawGraph(sixMonthData, chartTitle);
        // })


            // Create a chart
            var chart = LightweightCharts.createChart(document.getElementById('stock-graph'), {
                width: 1024,
                height: 400,
                allow_symbol_change: true,
                theme: "dark",
            });

            // Add a candlestick series
            var candlestickSeries = chart.addCandlestickSeries();

            // Fetch OHLCV data from your Flask route
            fetch('/read_full_stock_data')
                .then(response => response.json())
                .then(data => {
                    candlestickSeries.setData(data);
                })
                .catch(error => console.error('Error fetching data:', error));
       
   

    });

    // Add event listeners to buttons to display graph
    button1M.addEventListener("click", function() {
        graph.innerHTML = "";
        getStockChart(stockSymbol, '1m', function(sixMonthData, chartTitle) {
            drawGraph(sixMonthData, chartTitle);
        });
    });

    button3M.addEventListener("click", function() {
        graph.innerHTML = "";
        getStockChart(stockSymbol, '3m', function(sixMonthData, chartTitle) {
            drawGraph(sixMonthData, chartTitle);
        });
    });

    button6M.addEventListener("click", function() {
        graph.innerHTML = "";
        getStockChart(stockSymbol, '6m', function(sixMonthData, chartTitle) {
            drawGraph(sixMonthData, chartTitle);
        });
    });

    button1Y.addEventListener("click", function() {
        graph.innerHTML = "";
        getStockChart(stockSymbol, '1y', function(sixMonthData, chartTitle) {
            drawGraph(sixMonthData, chartTitle);
        });
    });

    button2Y.addEventListener("click", function() {
        graph.innerHTML = "";
        getStockChart(stockSymbol, '2y', function(sixMonthData, chartTitle) {
            drawGraph(sixMonthData, chartTitle);
        });
    });

    button5Y.addEventListener("click", function() {
        graph.innerHTML = "";
        getStockChart(stockSymbol, '5y', function(sixMonthData, chartTitle) {
            drawGraph(sixMonthData, chartTitle);
        });
    });

});

function getStockChart(symbol, timeRange, callback) {
    /* Make the AJAX request to the IEX API to get the data for a chart */
    var chartTitle = getChartTitle(timeRange)
    var stock_data = [];
            
            // Sample data for demonstration
            var sampleData = [
                { date: '2023-08-01', low: 150 },
                { date: '2023-08-02', low: 155 },
                { date: '2023-08-03', low: 148 },
                { date: '2023-08-04', low: 152 },
                { date: '2023-08-05', low: 158 },
                // Add more sample data as needed
            ];
            
            // Use sampleData for demonstration
            $.each(sampleData, function(i, price) {
                stock_data.push([price.date, price.low]);
            });
    
            callback(stock_data, chartTitle);
    
}

function drawGraph(data_set, title) {
    /* Draws the graph using anychart https://www.anychart.com/ */
    // create data set on our data
    var dataSet = anychart.data.set(data_set);

    // map data for the series, take x from the zero column and value from the first column of data set
    var seriesData = dataSet.mapAs({'x': 0, 'value': 1});

    // create line chart
    var chart = anychart.line();

    // turn on chart animation
    chart.animation(true);

    // set chart padding
    chart.padding([10, 20, 5, 20]);

    // turn on the crosshair
    chart.crosshair()
            .enabled(true)
            .yLabel(false)
            .yStroke(null);

    // set tooltip mode to point
    chart.tooltip().positionMode('point');

    // set chart title text settings
    chart.title(title);

    // set yAxis title
    chart.yAxis().title('Price in QAR');
    chart.xAxis().labels().padding(5);

    // create first series with mapped data
    var series = chart.line(seriesData);
    series.name('Price');
    series.hovered().markers()
            .enabled(true)
            .type('circle')
            .size(4);
    series.tooltip()
            .position('right')
            .anchor('left-center')
            .offsetX(5)
            .offsetY(5);

    // set container id for the chart
    chart.container('stock-graph');
    // initiate chart drawing
    chart.draw();
}


function getChartTitle(timeRange) {
    /* Sets the chart title */
    var chartTitle = "";
    switch(timeRange) {
        case '1m':
            chartTitle = 'One Month History';
            break;
        case '3m':
            chartTitle = 'Three Month History';
            break;
        case '6m':
            chartTitle = 'Six Month History';
            break;
        case '1y':
            chartTitle = 'One Year History'
            break;
        case '2y':
            chartTitle = 'Two Year History';
            break;
        case '5y':
            chartTitle = 'Five Year History';
    }
    return chartTitle;
}
