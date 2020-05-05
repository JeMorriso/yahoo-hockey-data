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

const getChartData = async _ => {
    const response = await fetch('http://localhost:3000/chart');
    const data = await response.json();
    return data;
}

// cannot use await here because not inside an async function
getChartData().then(data => {
    const chartData = buildChartData(data);

    flatpickr('#datepicker', {
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
        mode: "range",
        // maxDate doesn't work properly if not converted to Date first
        minDate: new Date(data.min_date),
        maxDate: new Date(data.max_date)
    });

    const myChart = new Chart(ctx, {
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

Chart.defaults.global.defaultFontSize = 16;

var ctx = document.getElementById('league-graph').getContext('2d');

