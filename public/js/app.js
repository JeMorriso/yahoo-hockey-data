var fp;

document.getElementById("form-submit").addEventListener("click", _ => {
  var start_date, end_date;

  console.log(fp.selectedDates);
  if (Array.isArray(fp.selectedDates) && fp.selectedDates.length) {
    start_date = fp.selectedDates[0].toISOString().substring(0,10);
    end_date = fp.selectedDates[1].toISOString().substring(0,10);
  }
  
  const result = document.getElementById("categories");
  // get the select element's selected option value
  const category = result.options[result.selectedIndex].text;
  console.log({ start_date, end_date, category });

  // update the chart
  getChartDataWrapper({ start_date, end_date, category });
});

document.getElementById("cumulative-checkbox").addEventListener("click", _ => {
  data = { labels: rawChartData.dates, datasets: [] }

  // build structure for each dataset entry (each line in graph)
  Object.entries(rawChartData.teamStats).forEach(([key, val], i) => {
      data.datasets.push({
          label: key,
          data: document.getElementById("cumulative-checkbox").checked == false ? val.rollingAverage : val.cumulative,
          borderColor: rawChartData.colours[i],
      })
  });
  myChart.destroy();
  var ctx = document.getElementById('league-graph').getContext('2d');

  myChart = generateChart(ctx, data, rawChartData.category)
});

const getMinMaxDates = async _ => {
  const response = await fetch('http://localhost:3000/flatpickr', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
  });
  const resData = await response.json();
  return resData;
}

getMinMaxDates().then(data => {
  fp = flatpickr('#datepicker', {
    altInput: true,
    altFormat: "F j, Y",
    dateFormat: "Y-m-d",
    mode: "range",
    // maxDate doesn't work properly if not converted to Date first
    minDate: new Date(data.min_date),
    maxDate: new Date(data.max_date)
  });
})



