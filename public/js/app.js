var fp;

// keeps track of the state of the chart radio buttons
let isCumulative = true;

document.getElementById('form-submit').addEventListener('click', (_) => {
  var start_date, end_date;

  console.log(fp.selectedDates);
  if (Array.isArray(fp.selectedDates) && fp.selectedDates.length) {
    start_date = fp.selectedDates[0].toISOString().substring(0, 10);
    end_date = fp.selectedDates[1].toISOString().substring(0, 10);
  }

  const result = document.getElementById('categories');
  // get the select element's selected option value
  const category = result.options[result.selectedIndex].text;
  console.log({ start_date, end_date, category });

  // update the chart
  getChartDataWrapper({ start_date, end_date, category });
  // reset the radio button to cumulative
});

const chartRadios = document.getElementsByName('chart-radio');
for (radio of chartRadios) {
  // remember that arrow function does not bind it's own 'this'
  radio.addEventListener('click', function (e) {
    data = { labels: rawChartData.dates, datasets: [] };
    isCumulative = this.id === 'cumulative' ? true : false;

    // build structure for each dataset entry (each line in graph)
    Object.entries(rawChartData.teamStats).forEach(([key, val], i) => {
      data.datasets.push({
        label: key,
        data: isCumulative ? val.cumulative : val.rollingAverage,
        borderColor: rawChartData.colours[i],
        hidden: teamsHidden[key],
      });
    });
    myChart.destroy();
    var ctx = document.getElementById('league-graph').getContext('2d');

    myChart = generateChart(ctx, data, rawChartData.category);
  });
}

const selectButtons = document.getElementsByClassName('select-button');
for (button of selectButtons) {
  button.addEventListener('click', function (e) {
    const hide = this.id === 'unselect-button' ? true : false;
    for (dataset of myChart.data.datasets) {
      dataset.hidden = hide;
      teamsHidden[dataset.label] = hide;
    }
    myChart.update();
  });
}

// utility functions
const getMinMaxDates = async (_) => {
  const response = await fetch(buildFetchURL('flatpickr'), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
  });
  const resData = await response.json();
  return resData;
};

const buildFetchURL = (route) => {
  return window.location.protocol + '//' + window.location.host + '/' + route;
};

getMinMaxDates().then((data) => {
  fp = flatpickr('#datepicker', {
    altInput: true,
    altFormat: 'F j, Y',
    dateFormat: 'Y-m-d',
    mode: 'range',
    // maxDate doesn't work properly if not converted to Date first
    minDate: new Date(data.min_date),
    maxDate: new Date(data.max_date),
  });
});
