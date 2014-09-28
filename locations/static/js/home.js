/**
 * Created by Andrew Brookins on Sep 27 9:31 PM 2014
 */
(function () {

  function getLocation () {
    navigator.geolocation.getCurrentPosition(function (location) {
      window.location = '/locations/compare-to-city-average/' + location.coords.longitude + '/' + location.coords.latitude;
    }, function (err) {
      alert('Could not get your location. Try enabling location services.');
      console.log(err);
    });
  }

  $('#compare-location').on('click', getLocation);
})();