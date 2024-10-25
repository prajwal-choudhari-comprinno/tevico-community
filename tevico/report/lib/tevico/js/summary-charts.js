const chartHeights = {
  'failed-by-severity': 240,
  'failed-by-service': 252,
  'failed-by-section': 255,
  'passed-by-severity': 240,
  'passed-by-service': 252,
  'passed-by-section': 255
};


// Failed by severity
document.addEventListener("DOMContentLoaded", function () {
  window.ApexCharts && (new ApexCharts(document.querySelector("#failed-by-severity"), {
    series: [{
      data: [27.27, 100, 41.67, 85.71]
    }],
    chart: {
      type: 'bar',
      height: chartHeights['failed-by-severity'],
      toolbar: {
        show: false
      }
    },
    plotOptions: {
      bar: {
        borderRadius: 4,
        horizontal: true,
        dataLabels: {
          position: 'bottom'
        }
      }
    },
    dataLabels: {
      enabled: true,
      formatter: function (val) {
        return `${val.toFixed(2)} %`;
      },
      style: {
        colors: ['#fff']
      },
      offsetX: 20
    },
    xaxis: {
      categories: [
        'Critical',
        'Low',
        'Medium',
        'High'
      ],
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false
      },
      labels: {
        show: false
      }
    },
    yaxis: {
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false
      }
    },
    grid: {
      show: false
    }
  })).render();
})

// Failed by service
document.addEventListener('DOMContentLoaded', function () {
  window.ApexCharts && (new ApexCharts(document.getElementById('failed-by-service'), {
    series: [44, 55, 41, 17, 15],
    chart: {
      height: chartHeights['failed-by-service'],
      type: 'donut',
    },
    responsive: [{
      options: {
        legend: {
          position: 'bottom'
        }
      }
    }]
  })).render();
});

// Failed by section
document.addEventListener('DOMContentLoaded', function () {
  window.ApexCharts && (new ApexCharts(document.getElementById('failed-by-section'), {
    series: [44, 55, 41, 17, 15],
    chart: {
      height: chartHeights['failed-by-section'],
      type: 'pie',
    },
    responsive: [{
      options: {
        legend: {
          position: 'bottom'
        }
      }
    }]
  })).render();
});


// Passed by severity
document.addEventListener("DOMContentLoaded", function () {
  window.ApexCharts && (new ApexCharts(document.querySelector("#passed-by-severity"), {
    series: [{
      data: [27.27, 100, 41, 85.71]
    }],
    chart: {
      type: 'bar',
      height: chartHeights['passed-by-severity'],
      toolbar: {
        show: false
      }
    },
    plotOptions: {
      bar: {
        borderRadius: 4,
        horizontal: true,
        dataLabels: {
          position: 'bottom'
        }
      }
    },
    dataLabels: {
      enabled: true,
      formatter: function (val) {
        return `${val.toFixed(2)} %`;
      },
      style: {
        colors: ['#fff']
      },
      offsetX: 20
    },
    xaxis: {
      categories: [
        'Critical',
        'Low',
        'Medium',
        'High'
      ],
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false
      },
      labels: {
        show: false
      }
    },
    yaxis: {
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false
      }
    },
    grid: {
      show: false
    }
  })).render();
});

// Passed by service
document.addEventListener('DOMContentLoaded', function () {
  window.ApexCharts && (new ApexCharts(document.getElementById('passed-by-service'), {
    series: [44, 55, 41, 17, 15],
    chart: {
      height: chartHeights['passed-by-service'],
      type: 'donut',
    },
    responsive: [{
      options: {
        legend: {
          position: 'bottom'
        }
      }
    }]
  })).render();
});


// Passed by section
document.addEventListener('DOMContentLoaded', function () {
  window.ApexCharts && (new ApexCharts(document.getElementById('passed-by-section'), {
    series: [44, 55, 41, 17, 15],
    chart: {
      height: chartHeights['passed-by-section'],
      type: 'pie',
    },
    responsive: [{
      options: {
        legend: {
          position: 'bottom'
        }
      }
    }]
  })).render();
});