$(document).ready(function() {
  $.getJSON("../predict_all/  ", function (json) {
    window.vanilla_json = json;
    make_tables();
  });

  function make_tables(){
    var index = 0, j = 0;

    empty_arr = [];
    full_arr = [];

    for (index = 0; index < window.vanilla_json["0"].length; index++){

      var obj = window.vanilla_json["60"][index];

      // Skipping things that do not have predictions
      if ((!obj["name"]) || (!obj["current_bikes"])){//|| !obj["prob_full"]) {
        continue;
      }
      if (obj["prob_empty"] >= .5) {
        empty_arr.push([obj["name"], obj["current_bikes"], obj["expected_num_bikes"], obj["prob_empty"]]);
      } else {
        full_arr.push([obj["name"], obj["current_bikes"], obj["expected_num_bikes"], obj["prob_full"]]);
      }
    }

    $('#empty').dataTable({
      "aaData": empty_arr,
      "aaSorting": [[ 2 , 'asc']],
      "aoColumns": [
      { "sTitle": "Name" },
      { "sTitle": "Current Bikes" },
      { "sTitle": "Expected Bikes" },
      { "sTitle": "% Chance to Stay Empty"}
    ]
    });


    $('#full').dataTable({
      "aaData": full_arr,
      "aaSorting": [[2, 'desc']],
      "aoColumns": [
      { "sTitle": "Name" },
      { "sTitle": "Current Bikes" },
      { "sTitle": "Expected Bikes" },
      { "sTitle": "% Chance to Stay Full"}
      ]
    });
}


});