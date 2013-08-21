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


      //
      var coords = [current_feature.lat, current_feature.lon];
      try {
        var p = parseFloat(current_feature.expected_num_bikes) / parseFloat(current_feature.max_slots);
        var weight = 4*((1.0 / 4.0) - p * (1 - p));
        // console.log(weight);
        var weight_index = Math.round(weight*10);
        var bigger_value = Math.max(current_feature.prob_empty, current_feature.prob_full);
        bigger_value = Math.round(bigger_value * 10);
        hexColor = MYAPP.make_gradients()[bigger_value];

        var circle_options = {
          color       : 'black', // Stroke color
          //opacity   : 1,          // Stroke opacity
          weight      : 2, // Stroke weight
          fillColor   : hexColor, // Fill color
          fillOpacity : 1 // Fill opacity
        };
        // circle_marker = L.pie(coords, [1,1]).addTo(MYAPP.map);
        var pie_parts = [current_feature.expected_num_bikes, current_feature.max_slots - current_feature.expected_num_bikes];
        circle_marker = L.pie(coords, pie_parts, {
            labels: false, 
            radius: 100,
            colors: ["#B8DC3C", "#CB2402"],
            pathOptions: {
              // clickable: false,
              riseOnHover: true,
              fillOpacity: 1

            }
          }).addTo(MYAPP.map);

        circle_marker.current_feature = current_feature;

        // var circle_marker = L.circle(coords, 50 + 20 * weight_index, circle_options).addTo(MYAPP.map.markerLayer);
      } catch (err) {
        console.log(err)
        continue;
      }

      circle_marker.addClick(popUp(current_feature));
      circle_marker.feature_properties = current_feature;

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

function popUp(properties){

  return function(){
    console.log(properties);
  }
};
