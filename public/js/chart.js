var myChart;

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
            fill: false,
            lineTension: 0
        })
    });
    return data;
}

// reqData is start_date, end_date, and category, or empty (first page load)
const getChartData = async reqData => {
    const response = await fetch('http://localhost:3000/chart', {
        // only post request can have body in fetch API
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reqData)
    });
    const resData = await response.json();
    return resData;
}

function getChartDataWrapper(reqData) {
    // cannot use await here because not inside an async function
    getChartData(reqData).then(data => {
        const chartData = buildChartData(data);

        if (myChart !== undefined) {
            myChart.destroy();
        }
        var ctx = document.getElementById('league-graph').getContext('2d');

        myChart = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            // y-axis starts at 0
                            beginAtZero: true
                        }
                    }]
                },
                // default true
                responsive: true,
                title: {
                    display: true,
                    text: data.category
                }
            }
        });
    });
}

getChartDataWrapper();
Chart.defaults.global.defaultFontSize = 16;
