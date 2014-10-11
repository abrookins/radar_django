(function() {

  function createDataTables(locationCrimeSums, cityAverages, crimeTypes) {
    var header = ['Crime type', 'Your location', 'City average'],
        data = {},
        crimeType,
        locationSum,
        i,
        cityAverage;

    crimeTypes.sort();

    for (i = 0; i < crimeTypes.length; i++) {
      crimeType = crimeTypes[i];
      locationSum = parseFloat(locationCrimeSums[crimeType] || 0);
      cityAverage = parseFloat(cityAverages[crimeType]);
      data[crimeType] = [header];
      data[crimeType].push([crimeType, locationSum, cityAverage]);
    }

    return data;
  }

  function createCrimeChart (data, elementId) {
    var dataTable,
        chart,
        options = {
          chartArea: {top: 40, bottom: 40},
          vAxis: {titleTextStyle: {color: 'red'}},
          hAxis: {title: "Crimes per year", titleTextStyle: {color: 'black'}}
        };

    dataTable = google.visualization.arrayToDataTable(data);
    chart = new google.visualization.BarChart(document.getElementById(elementId));
    chart.draw(dataTable, options);
  }

  function getData(coords) {
    var url = '/api/v1.0/crimes/compare/' + coords.longitude + '/' + coords.latitude + '/to/city-average/',
        chartContainer = $('#charts'),
        crimeType,
        crimeTypeDiv,
        crimes,
        id,
        data;

    $.get(url).then(function(response) {
      data = createDataTables(response.location_sums.by_type, response.city_averages, response.crime_types);


      for (crimeType in data) {
        if (data.hasOwnProperty(crimeType)) {
          id = crimeType.toLowerCase().replace(' ', '-');
          crimeTypeDiv = $("<div>")
              .height('200px')
              .width('900px')
              .attr('id', id);
          chartContainer.append(crimeTypeDiv);
          crimes = data[crimeType];
          createCrimeChart(crimes, id);
        }
      }
    }).fail(function(response) {
      alert("Could not connect to site. Try again later.");
      console.log(response);
    });
  }

  $(document).ready(function() {
    google.load("visualization", "1", {
      packages: ["corechart"],
      callback: function () {
        getData(window.coords);
      }
    });
  });
})();