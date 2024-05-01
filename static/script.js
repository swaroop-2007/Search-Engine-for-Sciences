var BASE_URL = "http://127.0.0.1:5000/api/v1/indexer"
var data = [];

function customEngine(input) {
    var countriesIFrame = document.getElementById("countries").contentWindow.document;    
    
    let frameElement = document.getElementById("countries");
    let doc = frameElement.contentDocument;
    doc.body.innerHTML = doc.body.innerHTML + '<style>a {margin: 0px 0px 0px 0px;}</style>';
    
    countriesIFrame.open();
    
    var out = "";
    var i;
     for(i = 0; i < data.length; i++) {
         out += '<a href="' + data[i].url + '">' +
         data[i].title + '</a><br>' + "<p>" + data[i].url + "<br>" +
         data[i].meta_info +"</p>";
    }
    countriesIFrame.write(out);
    
    countriesIFrame.close();
}

function queryToGoogleBing() {
    var input = document.getElementById("UserInput").value;
    document.getElementById("google").src = "https://www.google.com/search?igu=1&source=hp&ei=lheWXriYJ4PktQXN-LPgDA&q=" + input;
    document.getElementById("bing").src = "https://www.bing.com/search?q=" + input;
}

function search() {
    var input = document.getElementById("UserInput").value;
    
    var page_rank = document.getElementById("page_rank").checked;
    var hits = document.getElementById("hits").checked;
    var flat_clustering = document.getElementById("flat_clustering").checked;
    var singlelink_clustering = document.getElementById("singlelink_clustering").checked;
    var completelink_clustering = document.getElementById("completelink_clustering").checked;
    var association_qe = document.getElementById("association_qe").checked;
    var metric_qe = document.getElementById("metric_qe").checked;
    var scalar_qe = document.getElementById("scalar_qe").checked;
    var type;
    
    if (page_rank) {
        type = "page_rank";
    }
    else if (hits) {
        type = "hits";
    }
    else if (flat_clustering) {
        type = "flat_clustering";
    }
    else if (singlelink_clustering) {
        type = "singlelink_clustering";
    }
    else if (completelink_clustering) {
        type = "completelink_clustering";
    }
    else if (association_qe) {
        type ="association_qe";
    }
    else if (metric_qe) {
        type ="metric_qe";
    }
    else if (scalar_qe) {
        type ="scalar_qe";
    }
    
    // Check if query expansion option is selected
    if (association_qe || metric_qe || scalar_qe) {
        // Send request to server for query expansion
        $.get(BASE_URL, {"query": input, "type": type})
        .done(function(resp) {
            data = resp;
            customEngine(input);
            
            var expandedQuery = resp[20];
            console.log(expandedQuery);

            // Display query expansion result
            //var expandedQuery = resp.map(function(result) {
            //    return result.title; // Assuming 'title' is the relevant property of the query expansion result
            //}).join(' ');
            //console.log(result)
            var queryExpansionOutput = document.getElementById("query-expansion-output");
            queryExpansionOutput.innerHTML = expandedQuery;
            var queryExpansionResult = document.getElementById("query-expansion-result");
            queryExpansionResult.style.display = "block";
        })
        .fail(function(e) {
            console.log("error", e);
        });
    } else {
        // If no query expansion option selected, proceed with regular search
        $.get(BASE_URL, {"query": input, "type": type})
        .done(function(resp) {
            data = resp;
            customEngine(input);
        })
        .fail(function(e) {
            console.log("error", e);
        });
    }
}


function showQueryExpansion() {
    var resultDiv = document.getElementById("query-expansion-result");
    var output = document.getElementById("query-expansion-output");
    var radioButtons = document.getElementsByName("query-expansion");
    
    for (var i = 0; i < radioButtons.length; i++) {
        if (radioButtons[i].checked) {
            resultDiv.style.display = "block";
            output.innerHTML = "Query Expansion: " + radioButtons[i].value;
            return;
        }
    }
    
    resultDiv.style.display = "none";
}
