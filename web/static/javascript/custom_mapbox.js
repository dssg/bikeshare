$(document).ready(function(){
  // Just explicitly using window for global variables
  window.prediction_time = "0";

  $("#slider").slider({
    value : 0,
    min   : 0,
    max   : 4 * 60 - 15,  // hours * mins
    step  : 15,     // 15 min intervals, can change with model
    slide: function( event, ui ) {
      window.prediction_time  = ui.value.toString();
      $( "#time" ).text( "Mins From Now: " + ui.value );
      updateMarkerColorsAndAddGeoJSON();
    }
  });

  // Made TileMap with JSON with Vidhur's account
  var map = L.mapbox.map('map', 'darkzeroman.map-gxrlhgnw').whenReady(function(){
    // only load the json when the map is ready
    $.getJSON("../static/data/fullnewyork.geojson", function(json) {

      window.vanilla_json = json;

      updateMarkerColorsAndAddGeoJSON();

      // Below are mouseover/mouseout event listeners
      map.markerLayer.on('mouseover', function(e){
        var marker = e.layer, feature = marker.feature;

        var popupContent = String("name") + ' : ' + String(feature.properties["name"]) + ' <br> ';
        popupContent += 'For Time: ' + window.prediction_time + ' <br> ';
        for (key_name in feature.properties[window.prediction_time]){
          popupContent += String(key_name) + ' : ' + String(feature.properties[window.prediction_time][key_name]) + ' <br> ';
        }
        
        // http://leafletjs.com/reference.html#popup for more options
        marker.bindPopup(popupContent, {
          closeButton: false,
        });
        e.layer.openPopup();
      });

      map.markerLayer.on('mouseout', function(e){
        e.layer.closePopup();
      });
    });    
  });

  function updateMarkerColorsAndAddGeoJSON(){
    var index = 0;
    var json = window.vanilla_json;

    function rgbToHex(r, g, b) {
      function componentToHex(c) {
        var hex = c.toString(16);
        return hex.length == 1 ? "0" + hex : hex;
      };
      return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
    };

    console.log(window.prediction_time);

    // Setting the color, maybe this can be handled server side?
    for (index = 0; index < json.features.length; index++){
      var current_feature = json.features[index];

      var percentage_full = parseFloat(current_feature.properties[window.prediction_time].percentage_full);
      var percentage_empty = parseFloat(current_feature.properties[window.prediction_time].percentage_empty);

      var hex_color = rgbToHex(Math.round(percentage_full * 255), 128, Math.round(percentage_empty * 255));

      current_feature.properties['marker-color'] = hex_color;
    }

    map.markerLayer.setGeoJSON(json);        
    console.log("updating colors");

  };

});