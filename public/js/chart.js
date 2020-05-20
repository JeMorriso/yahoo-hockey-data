var myChart;
// save resData for frontend use
var rawChartData;
// status of team's data on chart - hidden or shown
var teamsHidden = {};

// reqData is start_date, end_date, and category, or empty (first page load)
const getChartData = async reqData => {
    const response = await fetch(buildFetchURL('chart'), {
        // only post request can have body in fetch API
        method: 'POST',
        headers: {
            // 'Accept': 'application/json',
            // posting JSON data
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
        // also add each key to teamsHidden object, only the first time the page is loaded to avoid overwriting
        if (Object.keys(teamsHidden).length < Object.keys(rawData.teamStats).length) {
            teamsHidden[key] = false;
        }

        data.datasets.push({
            label: key,
            data: val.cumulative,
            borderColor: rawData.colours[i],
            hidden: teamsHidden[key]
        });
    });
    return data;
}

const generateChart = (ctx, chartData, chartTitle) => {
    return new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            legend: {
                position: 'top',
                align: 'end',
                onHover: function(e) {
                    e.target.style.cursor = 'pointer';
                 },
                 onLeave: (e) => {
                     e.target.style.cursor = 'default';
                 }, 
                 onClick: function (e, legendItem) {  
                     console.log(legendItem);
                     teamsHidden[legendItem.text] = !teamsHidden[legendItem.text];
                     Chart.defaults.global.legend.onClick.call(this, e, legendItem);
                 }
                //  labels: {
                //      defaultFontStyle: 'monospace'
                //  }
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
            maintainAspectRatio: false,
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