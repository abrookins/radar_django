(function() {

  function createCrimeChart(data) {
    nv.addGraph(function () {
      var chart = nv.models.multiBarHorizontalChart()
          .x(function (d) {
            return d.label
          })
          .y(function (d) {
            return d.value
          })
          .margin({top: 30, right: 20, bottom: 50, left: 175})
          .showValues(true)           //Show bar value next to each bar.
          .tooltips(true)             //Show tooltips on hover.
          .transitionDuration(350)
          .showControls(false);        // Don't allow user to switch between "Grouped" and "Stacked" mode.

      d3.select('#chart1 svg')
          .datum(data)
          .call(chart);

      nv.utils.windowResize(chart.update);

      return chart;
    });

      $('#comparison').removeClass('hidden');
  }

  function getData(coords) {
    var url = '/api/v1.0/crimes/compare_location/' + coords.longitude + '/' + coords.latitude;
    $.get(url).then(function(averages) {
      var sorted = [],
          data = [{
            key: "Crime types compared to city average",
            values: []
          }],
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
        floatValue = parseFloat(item[1]);
        if (isNaN(floatValue)) {
          continue;
        }
        data[0].values.push({
          "label": item[0],
          "value": floatValue
        });
      }

      createCrimeChart(data);

    }).fail(function(response) {
      alert("Could not connect to site. Try again later.");
      console.log(response);
    });
  }

  function getLocation() {
    navigator.geolocation.getCurrentPosition(function(location) {
      getData(location.coords);
    }, function(err) {
      alert('Could not get your location. Try enabling location services.');
      console.log(err);
    });
  }


  $('#compare-location').on('click', getLocation);
})();