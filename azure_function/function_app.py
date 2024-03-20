import azure.functions as fns

app = fns.FunctionApp()

# keep these standalone...easier to change later
name = "Yelp Items"
desc = "Yelp passthrough service."


@app.route(route='')
def feature_service(res: fns.httpRequest) -> fns.httpResponse:
    """Main entry point providing information about the feature service."""

    # json payload
    json_res = {
        "hasStaticData" : "true",
        "supportedQueryFormats": "JSON",
        "capabilities": "Query",
        "description": desc,
        "copyrightText" : "",
        "spatialReference": {
            "wkid": 4326,
            "latestWkid": 4326
        },
        "initialExtent": {
            "xmin": -180.0,
            "ymin": -90.0,
            "xmax": 180.0,
            "ymax": 90.0,
            "spatialReference": {
                "wkid": 4326,
                "latestWkid": 4326
            }
        },
        "fullExtent": {
            "xmin": -180.0,
            "ymin": -90.0,
            "xmax": 180.0,
            "ymax": 90.0,
            "spatialReference": {
                "wkid": 4326,
                "latestWkid": 4326
            }
        },
        "units": "esriDecimalDegrees",
        "layers": [
            {
                "id": 0,
                "name": name,
                "parentLayerId": -1,
                "defaultVisibility": "true",
                "subLayerIds": "null",
                "minScale": 0,
                "maxScale": 0,
                "geometryType": "esriGeometryPoint"
            },
        ]
    }

    # assemble into response object
    res = fns.httpResponse(
        body=json_res,
        status_code=200,
        headers={"Content-Type": "application/json"}
    )

    return res


@app.route(route="0")
def feature_layer(req: fns.httpRequest) -> fns.httpResponse:
    """Actual feature layer providing access to the data."""

    # put together the json package
    json_res = {
        "serviceDescription" : desc, 
        "supportedQueryFormats" : "JSON", 
        "capabilities" : "Query", 
        "description" : desc, 
        "copyrightText" : "",
        "spatialReference" : {
            "wkid" : 4326, 
            "latestWkid" : 4326
        }, 
        "initialExtent" : {
            "xmin" : -180, 
            "ymin" : -90, 
            "xmax" : 180, 
            "ymax" : 90, 
            "spatialReference" : {
                "wkid" : 4326, 
                "latestWkid" : 4326
            }
        }, 
        "fullExtent" : {
            "xmin" : -180, 
            "ymin" : -90, 
            "xmax" : 180, 
            "ymax" : 90, 
            "spatialReference" : {
                "wkid" : 4326, 
                "latestWkid" : 4326
            }
        },
        "units" : "esriDecimalDegrees", 
        "layers" : [
            {
                "id" : 0, 
                "name" : name, 
                "parentLayerId" : -1, 
                "defaultVisibility" : "true", 
                "subLayerIds" : "null", 
                "minScale" : 0, 
                "maxScale" : 0, 
                "type" : "Feature Layer", 
                "geometryType" : "esriGeometryPoint"
            }
        ], 
        "tables" : []
    }

    # assembe the response
    res = fns.httpResponse(
        body=json_res,
        status_code=200,
        headers={"Content-Type": "application/json"}
    )

    return res


def get_param(req: fns.HttpRequest, param: str) -> str:
    """Get the parameter from either the payload or the url."""
    # try the body first
    val = req.params.get(param)

    # if not found in the body, try the url string
    val = req.route_params.get(param) if val is None

    return val


@app.route(route="0")
def feature_layer_query(req: fns.httpRequest) -> fns.httpResponse:
    """Passes query to Cosmos DB and returns results."""

    # pull out the where clause
    where = get_param('where')

    # if no where clause is provided throw an error
    if where is None:
        json_res = {'error': 'A valid where string is required.'}
        res = fns.HttpResponse(
            json_res, 
            status_code=400, 
            headers={"Content-Type": "application/json"}
        )

    # otherwise, process the request
    else:
        raise NotImplementedError()
    
    return res
