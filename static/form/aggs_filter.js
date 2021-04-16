function removeOptions(objSelect) {
    while (objSelect.options.length > 0)
        objSelect.options[0] = null;
}

// element_ids -- sont les outputs des boutons - ce que je récupère quand on clique sur un boutton //
var element_ids = ["metric_field", "metric_agg", "bucket_field", "bucket_agg"];

// getValues est la fonction qui dénombre et donc récupère tous les couples possibles de choix //
function getValues() {
    var values = {};
    for (var i = 0; i < element_ids.length; i++) {
      var element = document.getElementById(element_ids[i]);
      if (element != null) {
          values[element_ids[i]] = element.value;
      }
    }
    console.log(values);
    return values;
}


var childListMetricAgg = {
      "doc": ["Count"],
      "duration": ["Stats", "Average","Sum", "Min", "Max"],
      "start_date": ["Min", "Max"],
      "end_date": ["Min", "Max"]
};


function parentList_OnChange(objParentList) {
      var child1 = document.getElementById("metric_agg");

      // Remove all options from both child lists
      removeOptions(child1);

    // Lookup and get the array of values for child list 1, using the parents selected value
      var child1Data = childListMetricAgg[objParentList.options[objParentList.selectedIndex].value];

      // Add the options to child list 1
      if (child1Data) {
        for (var i = 0; i < child1Data.length; i++) {
            child1.options[i] = new Option(child1Data[i], child1Data[i]);
          }
        child1.options[0].defaultSelected = true
     }
}


function run() {
     // on récupère le choix des valeurs des bouttons //
    var values = getValues();

    // AJAX > to check //
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/agg_res", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function() {
      if (this.readyState == XMLHttpRequest.DONE && this.status == 200) {
        console.log(this.responseText);
        var objects = JSON.parse(this.responseText);
        console.log(objects);

        var table = document.getElementById("result");
        if (table != null) {
          table.innerHTML = "";

          for (var i = 0; i < objects.length; i++) {
            var object = objects[i];

            var tr = document.createElement("tr");
            var td = null;

            td = document.createElement("td");
            td.appendChild(document.createTextNode(object['country']));
            tr.appendChild(td);

            td = document.createElement("td");
            td.appendChild(document.createTextNode(object['province']));
            tr.appendChild(td);

            td = document.createElement("td");
            td.appendChild(document.createTextNode(object['description']));
            tr.appendChild(td);

            table.appendChild(tr);
          }
        }
      }
    }

    var params = "_="+ Math.floor(Date.now() / 1000);
    for (var key in values) {
      params += "&"+ key +"="+ values[key];
    }
    xhr.send(params);
}

var submit = document.getElementById("submit");
if (submit != null) {
    submit.addEventListener("click", run);
}

run();