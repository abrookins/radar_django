/**
 * Created by Andrew Brookins on Sep 27 9:31 PM 2014
 */
(function () {

  function getLocation () {
    navigator.geolocation.getCurrentPosition(function (location) {
      window.location = '/locations/compare/' + location.coords.longitude + '/' + location.coords.latitude + '/to/city-average/';
    }, function (err) {
      alert('Could not get your location. Try enabling location services.');
      console.log(err);
    });
  }

  $('#compare-location').on('click', getLocation);
})();