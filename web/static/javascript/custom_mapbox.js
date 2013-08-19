MYAPP = {};
$(document).ready(function(){

  window.marker_arr = [];
  // Just explicitly using window for global variables
  window.prediction_time = "0";

  $("#slider").slider({
    value : 0,
    min   : 0,
    max   : 4 * 60 - 15,  // hours * mins
    step  : 15,     // 15 min intervals, can change with model
  }).on('slide', function(event, ui) {
      console.log(ui);
      window.prediction_time  = ui.value + "";
      $( "#time" ).text( "Mins From Now: " + ui.value );
      updateMarkerColorsAndAddGeoJSON();
  });


  // Made TileMap with JSON with Vidhur's account
  // darkzeroman.map-gxrlhgnw
  // darkzeroman.map-bi97back
  window.map = L.mapbox.map('map', 'darkzeroman.map-bi97back').whenReady(function(){
    // only load the json when the map is ready
    $.getJSON("../predict_all/10", function(json) {
      window.vanilla_json = json;
      updateMarkerColorsAndAddGeoJSON();
    });    
  });

  map.invalidateSize();

  function updateMarkerColorsAndAddGeoJSON(){

    var index = 0;
    var json = window.vanilla_json;

    // removing current markers
    for (index = 0; index < window.marker_arr.length; index++){
      window.map.removeLayer(window.marker_arr[index])
    }
    window.marker_arr = [];

    function rgbToHex(r, g, b) {
      function componentToHex(c) {
        var hex = c.toString(16);
        return hex.length == 1 ? "0" + hex : hex;
      };
      return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
    };

    // Setting the color, maybe this can be handled server side?
    for (index = 0; index < json.predictions.length; index++){

      console.log(json.predictions[index]);

      var current_feature = json.predictions[index];

      if (current_feature[1] == "Prediction Error"){
        continue;
      }


      // var hex_color = rgbToHex(Math.round(percentage_full * 255), 128, Math.round(percentage_empty * 255));

      var circle_options = {
        color       : 'red',      // Stroke color
        //opacity   : 1,          // Stroke opacity
        //weight    : 1,          // Stroke weight
        fillColor   : "#fff",  // Fill color
        fillOpacity : 1           // Fill opacity
      };

      //
      var coords = [current_feature.lat, current_feature.lon];
      var temp_circle = L.circle(coords, 200*.5, circle_options).addTo(map.markerLayer);
      temp_circle.feature_properties = current_feature;

      window.marker_arr.push(temp_circle);

      // Below are mouseover/mouseout event listeners
      temp_circle.on('mouseover', function(e){
        var feature = e.target.feature_properties;

        var popupContent = 'For Time: ' + 'None' + ' <br> ';
        for (key_name in feature){
          popupContent += String(key_name) + ' : ' + String(feature[key_name]) + ' <br> ';
        }
        
        // http://leafletjs.com/reference.html#popup for more options
        e.target.bindPopup(popupContent, {closeButton: false, autoPan: false}).openPopup();
      });

      temp_circle.on('mouseout', function(e){e.target.closePopup();});
    }
  };

});