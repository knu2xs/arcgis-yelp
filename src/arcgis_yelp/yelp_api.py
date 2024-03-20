from datetime import datetime
import json
import os
from typing import List, Optional, Tuple

from azure.cosmos import CosmosClient
import h3
import pandas as pd
from requests import Session

# bootstrapping some variables
yelp_client_id = os.getenv('YELP_CLIENT_ID')
yelp_api_key = os.getenv('YELP_API_KEY')

yelp_api_root = 'https://api.yelp.com/v3'
yelp_search_url = yelp_api_root + '/businesses/search'
yelp_details_url = yelp_api_root + '/businesses/'


def add_h3_index(yelp_item: dict, h3_resolution: int = 9) -> dict:
    
    # get the h3 index
    h3_idx = h3.latlng_to_cell(yelp_item.get('coordinates').get('latitude'), yelp_item.get('coordinates').get('longitude'), h3_resolution)
    
    # add the h3 index
    yelp_item[f'h3_{h3_resolution:02d}'] = h3_idx
    
    return yelp_item


def add_geometry(yelp_item: dict, format: str = 'arcgis') -> dict:
    """
    Add Point Geometry to a Yelp Item.

    Args:
        yelp_item: Dictionary representing a Yelp item returned from the Yelp Search API.
        format: Either `'arcgis'` or `'geojson'` add either ArcGIS Python API Point Geometry or GeoJSON dictionary geometry.
    """
    
    # get the coordinates
    coord_x = yelp_item.get('coordinates').get('longitude')
    coord_y = yelp_item.get('coordinates').get('latitude')
    
    # if arcgis, create ArcGIS Point geometry
    if format == 'arcgis':
        
        # late import just in case not in environment with arcgis
        from arcgis.geometry import Point

        pt = Point({'x': coord_x, 'y': coord_y, 'spatialReference' : {'wkid' : 4326}})
    
    # if geojson, do that
    elif format == 'geojson':
        
        pt = {
          "type": "Point",
          "coordinates": [coord_x, coord_y]
        }

    # add to the Yelp item
    yelp_item['geometry'] = pt
    
    return yelp_item


def enhance_response_list(yelp_list: List[dict], h3_resolutions: Tuple[int, int] = (4, 10), geometry_type: str = 'geojson'):
    """
    Add columns providing functionality and context.
    """
    # add the level h3 level 7 through 11 indices
    for h3_lvl in range(h3_resolutions[0], h3_resolutions[1]+1):
        yelp_list = [add_h3_index(yelp_itm, h3_lvl) for yelp_itm in yelp_list]

    # add ArcGIS Python API point geometry
        yelp_list = [add_geometry(yelp_itm, format="geojson") for yelp_itm in yelp_list]

    # get a string formatted address for display
    for yelp_item in yelp_list:
        loc = yelp_item.get('location')
        if loc is not None:
            yelp_item['address'] = ', '.join(loc.get('display_address'))

    # add retrieval timestamp
    dt_now = datetime.now().isoformat()
    for itm in yelp_list:
        itm['retrieval_timestamp'] = dt_now

    return yelp_list


class YelpSession(Session):
    """`requests.Session` wrapped with credentials embedded in the header to use for interfacting with the Yelp Fusion API."""

    root_url = 'https://api.yelp.com/v3'
    search_url = yelp_api_root + '/businesses/search'
    details_url = yelp_api_root + '/businesses/'

    def __init__(self, yelp_api_key: Optional[str] = None) -> Session:
        """
        Args:
            yelp_api_key: Yelp Fusion API key.
        """
        # if not provided, try to get the api key from the environment variables
        if yelp_api_key is None:
            self._api_key = os.getenv('YELP_API_KEY')
        else:
            self._api_key = yelp_api_key

        # pitch a fit if no key is available
        if self._api_key is None:
            raise ValueError('You must either set "YELP_API_KEY" as an environmenet variable or explicitly pass in the "yelp_api_key" parameter.')
        
        # set the headers per the requirements of the Yelp Fusion API
        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self._api_key}'
        }

    def search(self, longitude: float, latitude: float, limit: int = 50, sort_by: str = 'distance', radius: int = 1600, 
               term: str = 'food, bar', **kwargs) -> List[dict]:
        """
        Wrapper for search method in the Yelp Fusion API.
        https://docs.developer.yelp.com/reference/v3_business_search

        .. note::
            All arguments are described in the Yelp help docs. Any parameters detailed in the Yelp documentation can be passed in as 
            well, and will be blindly passed along to the Search REST endpoint.
        """
        # validate sort_by parameter
        sort_lst = ['best_match', 'rating', 'review_count', 'distance']
        if sort_by not in sort_lst:
            raise ValueError(f'"sort_by" parameter must be one of {sort_lst}. You provided "{sort_by}"')
        
        # initialize the params with known input parameters
        params = {
            'limit': limit,
            'sort_by': sort_by,
            'radius': radius,  # straight-line distance in meters
            'longitude': longitude,
            'latitude': latitude,
            'term': term
        }

        # add on any other parameters provided in kwargs
        params.update(kwargs)

        # make the get request to the Search endpoint of the Yelp Fusion API
        res = self.get(self.search_url, params=params)

        # minimal error catching
        if res.status_code == 400:
            raise RuntimeError(f'400 response received from Yelp Search./n{res.json()["error"]}')
        elif res.status_code != 200:
            raise RuntimeError(f'{res.status_code} response received from Yelp Searc./n{res.text}')
        
        # get the list of businesses from the request
        itm_lst = res.json().get('businesses')

        return itm_lst
