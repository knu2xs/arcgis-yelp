# arcgis-yelp

Accessing the Yelp API in conjunction with ArcGIS

## References

* [Azure Cosmos Client](https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python)
* [Azure Cosmos DB Spatial](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-geospatial-index-query)
* [Indexing Spatial Data in Cosmos DB NoSQL](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-geospatial-index-query#create-container-and-indexing-policy)
* [Using spatial geometry data in Azure Cosmos DB](https://devblogs.microsoft.com/cosmosdb/spatial-geometry-data/)
* [ST_INTERSECTS](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/query/st-intersects)
* [Geoservices Specification](http://geoservices.github.io) - basis for ArcGIS Feature Services

## BumpVersion Cliff Notes

[Bump2Version](https://github.com/c4urself/bump2version) is preconfigured based on hints from [this article on Medium](https://williamhayes.medium.com/versioning-using-bumpversion-4d13c914e9b8).

If you want to...

- apply a patch, `bumpversion patch`
- update version with no breaking changes (minor version update), `bumpversion minor`
- update version with breaking changes (major version update), `bumpversion major`
- create a release (tagged in vesrion control - Git), `bumpversion --tag release`

<p><small>Project based on the <a target="_blank" href="https://github.com/knu2xs/cookiecutter-geoai">cookiecutter GeoAI project template</a>. This template, in turn, is simply an extension and light modification of the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
