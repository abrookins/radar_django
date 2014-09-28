(function() {
  function createCrimeChart(data) {

    google.load("visualization", "1", {
      packages: ["corechart"],
      callback: drawChart
    });

    function drawChart () {
      var dataTable,
          options = {
            height: 800,
            chartArea: {top: 40},
            hAxis: {format: '#\'%\''}
          };

      var chart = new google.visualization.BarChart(document.getElementById('chart1'));

      dataTable = google.visualization.arrayToDataTable(data);
      chart.draw(dataTable, options);
    }

  }

  function getData(coords) {
    var url = '/api/v1.0/crimes/compare_location/' + coords.longitude + '/' + coords.latitude;
    $.get(url).then(function(averages) {
      var sorted = [],
          data = [
              ['Crime type', 'Percentage difference']
          ],
          crimeType,
          item,
          floatValue,
          i;

      for (crimeType in averages) {
        if (averages.hasOwnProperty(crimeType)) {
          sorted.push([crimeType, averages[crimeType]]);
        }
      }

      sorted.sort();

      for (i = 0; i < sorted.length; i++) {
        item = sorted[i];
        floatValue = parseInt(item[1]);
        if (isNaN(floatValue)) {
          continue;
        }
        data.push([item[0], floatValue])
      }

      createCrimeChart(data);

    }).fail(function(response) {
      alert("Could not connect to site. Try again later.");
      console.log(response);
    });
  }

  $(document).ready(function() {
    getData(window.coords);
  });
})();