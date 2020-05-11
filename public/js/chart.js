var myChart;
// save resData for frontend use
var rawChartData;

// reqData is start_date, end_date, and category, or empty (first page load)
const getChartData = async reqData => {
    const response = await fetch('https://in-it-to-winnik.herokuapp.com/chart', {
    // const response = await fetch('http://localhost:3000/chart', {
        // only post request can have body in fetch API
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reqData)
    });
    const resData = await response.json();
    rawChartData = resData;
    return resData;
}

// use data provided from AJAX request to build chart
// function expressions are NOT hoisted, so this must appear above any calling code
const buildChartData = rawData => {
    data = { labels: rawData.dates, datasets: [] }

    // build structure for each dataset entry (each line in graph)
    Object.entries(rawData.teamStats).forEach(([key, val], i) => {
        data.datasets.push({
            label: key,
            data: val.cumulative,
            borderColor: rawData.colours[i],
        })
    });
    return data;
}

const generateChart = (ctx, chartData, chartTitle) => {
    return new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            legend: {
                position: 'left',
                onHover: function(e) {
                    e.target.style.cursor = 'pointer';
                 },
                 onLeave: (e) => {
                     e.target.style.cursor = 'default';
                 }
            },
            scales: {
                yAxes: [{
                    ticks: {
                        // y-axis starts at 0
                        // beginAtZero: true
                    }
                }]
            },
            // default true
            responsive: true,
            title: {
                display: true,
                text: chartTitle,
                fontSize: 24
            }
        }
    });
}

function getChartDataWrapper(reqData) {
    getChartData(reqData).then(data => {
        const chartData = buildChartData(data);

        if (myChart !== undefined) {
            myChart.destroy();
        }
        var ctx = document.getElementById('league-graph').getContext('2d');

        myChart = generateChart(ctx, chartData, data.category)
    });
}

getChartDataWrapper();
Chart.defaults.global.defaultFontSize = 16;
Chart.defaults.global.elements.line.tension = 0;
Chart.defaults.global.elements.line.fill = false;
Chart.defaults.global.elements.point.hitRadius = 10;