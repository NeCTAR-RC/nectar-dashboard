var usageTrend = (function() {

  var usage = {};
  var trend_chart = {};
  var instance_chart = {};
  var instance_table = {};
  var begin_date = "";
  var end_date = "";

  function getInstanceData() {
    var api_url = "/api/nectar/usage/most-used/instance/?begin=" + begin_date + "&end=" + end_date;

    return new Promise((resolve, reject) => {
      $.ajax({
        url: api_url,
        type: 'GET',
        success: function (data) {
          // Is data object empty?
          if($.trim(data.data)) {
            resolve(data)
          }
          else {
            reject("Data empty!");
          }
        },
        error: function (error) {
          reject(error)
        },
      });
    });
  }

  function getTrendData() {
    var api_url = "/api/nectar/usage/summary/instance/?begin=" + begin_date + "&end=" + end_date + "&groupby=time-1d&detailed=True";

    return new Promise((resolve, reject) => {
      $.ajax({
        url: api_url,
        type: 'GET',
        success: function (data) {
          // Is data object empty?
          if($.trim(data.data)) {
            resolve(data)
          }
          else {
            reject("Data empty!");
          }
        },
        error: function (error) {
          reject(error)
        },
      });
    });
  }

  /* Private function to format the instance pie chart data to expects chartjs format */
  function formatPieChartData(object_data) {

    const coloursArr = ["#00A2C4", "#E51875", "#F8B20E", "#8E489B", "#969696", "#666666"];

    let new_format = {
      datasets: [{
        backgroundColor: [],
        data: []
      }],
      labels: []
    };

    let i = 0;

    object_data.forEach(item => {
      new_format.datasets[0].backgroundColor.push(coloursArr[i]);
      new_format.datasets[0].data.push(Object.values(item)[0]);
      new_format.labels.push(Object.keys(item)[0]);
      i++;
    });

    return new_format;
  }

  /* Private function to format the trend line chart data to expects chartjs format */
  function formatLineChartData(object_data) {

    let new_format = {
      datasets: [{
        label: 'Service Unit Daily Usage',
        backgroundColor: 'rgb(0, 130, 157)',
        borderColor: 'rgb(0, 130, 157)',
        pointRadius: 2,
        pointHoverRadius: 4,
        data: object_data,
      }],
      labels: []
    };
    object_data.forEach(item => {
      new_format.labels.push(item.begin);
    });

    return new_format;
  }

  function updateTotal(su_total) {
    $("#su_total").text(su_total);
  }

  function addData(chart, labels, dataset, count) {
    chart.data.datasets.push(dataset);
    chart.data.labels = labels;
    if(count) {
      chart.options.plugins.title.text = "There were " + count + " instances running";
    }
    chart.update();
  }

  function removeData(chart) {
    chart.data.datasets.pop();
    chart.data.labels = [];
    chart.update();
  }

  function updateChart(chart, labels, dataset, count = null) {
    removeData(chart);
    addData(chart, labels, dataset, count);
  }

  function createTrendChart(trend_data) {

    const chart_data = formatLineChartData(trend_data.data);
    const su_total = trend_data.sum;
    updateTotal(su_total);

    const chart_config = {
      type: 'line',
      data: chart_data,
      options: {
        responsive: true,
        scales: {
          xAxis: {
            type: 'time',
            time: {
              unit: 'day',
              displayFormats: {
                'day': 'MMM DD'
              }
            },
            title: {
              display: true,
              text: 'Date',
            }
          },
          yAxis: {
            suggestedMin: 0,
            title: {
              display: true,
              text: 'Service Units'
            }
          }
        },
        parsing: {
          xAxisKey: 'begin',
          yAxisKey: 'rate'
        }
      }
    };

    // Display the chart
    trend_chart = new Chart(
      document.getElementById('trend_chart').getContext('2d'),
      chart_config
    );
  }

  function createInstanceChart(instance_data) {

    const chart_data = formatPieChartData(instance_data.data);
    const instance_total = instance_data.count;

    const chart_config = {
      type: 'pie',
      data: chart_data,
      plugins: [ChartDataLabels],
      options: {
        plugins: {
          title: {
            display: true,
            text: 'There were ' + instance_total + ' instances running',
            font: {
              size: "16px"
            }
          },
          legend: {
            display: true,
            position: 'right',
            labels: {
              textAlign: 'left',
              generateLabels: (chart) => {
                if(chart.data.datasets[0]) {
                  const datasets = chart.data.datasets;
                  return datasets[0].data.map((data, i) => ({
                    text: `${chart.data.labels[i]}: ${data} SU`,
                    fillStyle: datasets[0].backgroundColor[i],
                    lineWidth: 0,
                  }));
                }
              }
            }
          },
          datalabels: {
            formatter: (value, ctx) => {
              if(ctx.chart.data.datasets[0]) {
                let sum = 0;
                let dataArr = ctx.chart.data.datasets[0].data;
                dataArr.map(data => {
                    sum += data;
                });
                let percentage = (value*100 / sum).toFixed(2);
                let labelToDisplay = percentage >= 8 ? percentage + "%" : "";
                return labelToDisplay;
              }
            },
            color: '#fff',
            font: {
              weight: 'bold'
            }
          }
        }
      }
    };

    // Display the chart
    instance_chart = new Chart(
      document.getElementById('instance_chart').getContext('2d'),
      chart_config
    );
  }

  /* Private function to render the instance pie chart */
  function displayInstanceChart() {
    getInstanceData()
      .then((data) => {
        if(instance_chart instanceof Chart) {
          console.log("Updating Instance chart...");
          const pie_chart_data = formatPieChartData(data.data);
          const new_dataset = pie_chart_data.datasets[0];
          const new_labels = pie_chart_data.labels;
          const instance_count = data.count;
          updateChart(instance_chart, new_labels, new_dataset, instance_count);
        }
        else {
          createInstanceChart(data);
        }
        $(".usage-error").hide();
        $(".chart-description").show();
        $(".usage-chart").show();
      })
      .catch((error) => {
        console.log(error);
        if(error === "Data empty!") {
          $(".usage-chart").hide();
          $(".chart-description").hide();
          $(".usage-error").show();
        }
      });
  }

  /* Private function to render the trend line chart */
  function displayTrendChart() {
    getTrendData()
      .then((data) => {
        if(trend_chart instanceof Chart) {
          console.log("Updating trend chart...");
          const line_chart_data = formatLineChartData(data.data);
          const new_dataset = line_chart_data.datasets[0];
          const new_labels = line_chart_data.labels;
          const su_total = data.sum;
          updateChart(trend_chart, new_labels, new_dataset);
          updateTotal(su_total);
        }
        else {
          createTrendChart(data);
        }
        $(".usage-error").hide();
        $(".usage-chart").show();
      })
      .catch((error) => {
        console.log(error);
        if(error === "Data empty!") {
          $(".usage-error").show();
          $(".usage-chart").hide();
        }
      });
  }

  function updateInstanceTable(url) {
    instance_table.ajax.url(url).load();
  };

  function createInstanceTable(url) {

    instance_table = $('#usage_table').DataTable({
      'responsive': true,
      'ajax': {
        'url': url,
        'dataSrc': ''
      },
      'columns': [
        { 'data': 'id', defaultContent: '' },
        { 'data': 'display_name', defaultContent: '' },
        { 'data': 'started_at', defaultContent: '' },
        { 'data': 'ended_at', defaultContent: '' },
        { 'data': 'availability_zone', defaultContent: '' },
        { 'data': 'flavor_name', defaultContent: '' },
        { 'data': 'qty', defaultContent: '' },
        { 'data': 'rate', defaultContent: '' },
      ],
      'order': [[ 5, 'desc' ]],
      'columnDefs': [
        {
          'targets': [2, 3],
          "orderable": false,
          'render': function ( data, type, row ) {
            if(data) {
              return (moment(data).format("DD/MM/YYYY"));
            }
          }
        }
      ]
    });

    console.log("Table Created!");
  }

  /* Private function to activate the datatable */
  function displayUsageTable() {
    var api_url = "/api/nectar/usage/instance-data/?begin=" + begin_date + "&end=" + end_date;

    if(instance_table instanceof $.fn.dataTable.Api) {
      console.log("Updating instance table...");
      updateInstanceTable(api_url);
    }
    else {
      console.log("Creating instance table...");
      createInstanceTable(api_url);
    }
  }

  /* Public function to get data and display charts for date range */
  usage.showDataWithRange = function(begin, end) {

    begin_date = begin;
    end_date = end;

    displayUsageTable();
    displayTrendChart();
    displayInstanceChart();
  }
  // Return public functions
  return usage;
}());

var usageOverview = (function() {

  var usage = {};
  var begin_date = "";
  var end_date = "";

  function formatLineChartData(object_data) {

    let new_format = {
      datasets: [{
        label: 'Service Unit Daily Usage',
        backgroundColor: 'rgb(0, 130, 157)',
        borderColor: 'rgb(0, 130, 157)',
        pointRadius: 2,
        pointHoverRadius: 4,
        data: object_data,
      }],
      labels: []
    };

    object_data.forEach(item => {
      new_format.labels.push(item.begin);
    });

    return new_format;
  }

  function getUsageData() {
    var api_url = "/api/nectar/usage/summary/instance/?begin=" + begin_date + "&end=" + end_date + "&groupby=time-1d&detailed=True";

    return new Promise((resolve, reject) => {
      $.ajax({
        url: api_url,
        type: 'GET',
        success: function (data) {
          // Is data object empty?
          if($.trim(data.data)) {
            resolve(data);
          }
          else {
            reject("Data empty!");
          }
        },
        error: function (error) {
          reject(error);
        },
      });
    });
  }

  function createUsageChart(trend_data) {

    const chart_data = formatLineChartData(trend_data.data);
    const su_total = trend_data.sum;

    // Display the total value on the page
    $("#su_total").text(su_total);

    const chart_config = {
      type: 'line',
      data: chart_data,
      options: {
        responsive: true,
        scales: {
          xAxis: {
            type: 'time',
            time: {
              unit: 'day',
              displayFormats: {
                'day': 'MMM DD'
              }
            },
            title: {
              display: true,
              text: 'Date',
            }
          },
          yAxis: {
            suggestedMin: 0,
            title: {
              display: true,
              text: 'Service Units'
            }
          }
        },
        parsing: {
          xAxisKey: 'begin',
          yAxisKey: 'rate'
        }
      }
    };

    // Display the chart
    trend_chart = new Chart(
      document.getElementById('usage_chart').getContext('2d'),
      chart_config
    );
  }

  /* Public function to render the trend line chart */
  function displayUsageChart() {
    getUsageData()
      .then((data) => {
        createUsageChart(data); 
        $(".usage-error").hide();
        $(".usage-chart").show();
      })
      .catch((error) => {
        console.log(error);
        if(error === "Data empty!") {
          $(".usage-error").show();
          $(".usage-chart").hide();
        }
      });
  }

  /* Public function to get data for past 3 months and display chart */
  usage.showUsage = function(begin, end) {
    begin_date = begin;
    end_date = end;

    displayUsageChart();
  }

  return usage;
}());

var usageAllocation = (function() {

  var usage = {};

  /* Public function to get data for past 3 months and display chart */
  usage.showUsage = function(cumulative_data, guide_data) {

    const data_cumulative = {
      datasets: [
        {
          label: 'Instance Service Unit Usage',
          data: cumulative_data,
          backgroundColor: 'rgb(0, 130, 157)',
          borderColor: 'rgb(0, 130, 157)',
          // pointBackgroundColor: function(context) {
          //     var index = context.dataIndex;
          //     var value = context.dataset.data[index].rate;
          //     var guide_point = 1000;
          //     return value > guide_point ? 'rgb(229, 24, 117)' : 'rgb(0, 130, 157)'; // need to change this to calculated guide value
          // },
          pointRadius: 0.5,
          pointHoverRadius: 2,
        },
        {
          label: 'Usage guide',
          data: guide_data,
          borderColor: 'rgb(150, 150, 150)',
          borderDash: [10,5]
        }
      ]
    };

    const config_cumulative = {
      type: 'line',
      data: data_cumulative,
      options: {
        plugins: {
          legend: {
            labels: {
              font: {
                  weight: "bold"
              }
            }
          }
        },
        scales: {
          xAxis: {
            display: true,
            type: 'time',
            time: {
              unit: 'month'
            },
            title: {
              display: true,
              text: 'Date',
              weight: "bold"
            }
          },
          yAxis: {
            display: true,
            suggestedMin: 0,
            title: {
              display: true,
              text: 'Service Units',
              weight: "bold"
            }
          }
        },
        parsing: {
            xAxisKey: 'begin',
            yAxisKey: 'rate'
        }
      }
    };

    const cumulative_chart = new Chart(
      document.getElementById('cumulative_chart'),
      config_cumulative
    );
  }

  // Return public functions
  return usage;
}());