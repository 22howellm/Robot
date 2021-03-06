/* This helper function sends and receive JSON to a server so to avoid a page refresh
urlstring, methodstring="GET"or"POST", parameterobject={var1:value,var1:value}, crossdomain=true or false, responsehandler=functionname */
function AJAX_request(urlstring, methodstring, responsehandler=defaulthandler, parametersobject=null, sendtype="json", crossdomainbool=false )
{
    $(document).ready(function() { //make sure script is fully loaded, otherwise errors will occur
        $.ajax({
            type: methodstring,
            headers: { 'Access-Control-Allow-Origin': '*' },
            crossDomain: crossdomainbool, //THIS IS REQUIRED IF COMMUNICATING TO NON-LOCAL SERVER
            url: urlstring,
            data: parametersobject, //{var1:1,var2:"hello"} //like a Python Dictionary
            dataType : sendtype,  //calls json.parse to convert results (JSON) to Javascript Object
            success: function(result) {
                responsehandler(result); //send results to responsehandler function
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
}

//function responsehandler, by default receives the results object which has been converted from JSON
function defaulthandler(results)
{
    console.log(results.message);
}