$(document).ready(function () {

  MYAPP.marker_arr = [];
  MYAPP.prediction_time = "0";

  $("#slider").slider({
    value: 0,
    min: 0,
    max: 120, // hours * mins
    step: 15, // 15 min intervals, can change with model
  }).on('slide', function (event, ui) {
    MYAPP.prediction_time = ui.value + "";
    $("#time").text("Mins From Now: " + ui.value);
    updateMarkers();
  });


  // Made TileMap with JSON with Vidhur's account
  // darkzeroman.map-gxrlhgnw : NYC MAP
  MYAPP.map = L.mapbox.map('map', 'darkzeroman.map-bi97back').whenReady(function () {
    // only load the json when the map is ready
    $.getJSON("../predict_all/  ", function (json) {
      MYAPP.vanilla_json = json;
      updateMarkers();
    });
  });

  function updateMarkers() {
    var index = 0;

    // removing current markers
    for (index = 0; index < MYAPP.marker_arr.length; index++) {
      MYAPP.map.removeLayer(MYAPP.marker_arr[index])
    }
    MYAPP.marker_arr = [];

    // Setting the color, maybe this can be handled server side?
    for (index = 0; index < MYAPP.vanilla_json[MYAPP.prediction_time].length; index++) {
      var json = MYAPP.vanilla_json[MYAPP.prediction_time];

      var current_feature = json[index];

      if (current_feature[1] == "Prediction Error") {
        continue;
      }

      var coords = [current_feature.lat, current_feature.lon];

      try {
        var p = parseFloat(current_feature.expected_num_bikes) / parseFloat(current_feature.max_slots);
        var weight = 4*((1.0 / 4.0) - p * (1 - p));
        var data = [current_feature.expected_num_bikes, current_feature.max_slots - current_feature.expected_num_bikes];
        weight_index = Math.round(weight*10);
        var colors = ["#DF151A", "#00DA3C"]


        // var colors = [MYAPP.make_gradients()[weight_index], ]
        var pieOptions = {
          labels: false,
          radius: 100,
          colors: colors,
          pathOptions: {
            fillOpacity: 1,
            color: 'black',
            weight: 1
          }

        }

        var circle_marker = L.pie(coords, data, pieOptions).addTo(MYAPP.map);
        var hexColor = MYAPP.make_gradients()[weight_index];
        
      } catch (err) {
        console.log(err)
        continue;
      }

      circle_marker.feature_properties = current_feature;

      MYAPP.marker_arr.push(circle_marker);

      // Below are mouseover/mouseout event listeners
      // circle_marker.on('mouseover', MYAPP.marker_mouseover);
      // circle_marker.on('mouseout', MYAPP.marker_mouseout);
      
    }
  };

});