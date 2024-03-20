import logging
from typing import List

import h3
from requests import Session, RequestException

__all__ = [
    "Yelp",
]

yelp_client_id = 'ZAyA5LhP0CVLQ3sJwFX2SA'
yelp_api_key = 'SDXO_3tR2DH1XbHCDKjKZ11q_TixjKnKicvLMKSa5CuPE3guusBwatV50ETtmxLrJRBk6g2EkUQTI1FY4Jni_7enVDUF2g19IrcAzE3xaqOLyB0sUFFIMtT4NrX3WXYx'

def add_h3_index(yelp_item: List[dict], h3_resolution: int = 9) -> List[dict]:
    
    # get the h3 index
    h3_idx = h3.latlng_to_cell(yelp_item.get('coordinates').get('latitude'), yelp_item.get('coordinates').get('longitude'), h3_resolution)
    
    # add the h3 index
    yelp_item[f'h3_{h3_resolution:02d}'] = h3_idx
    
    return yelp_item

def add_geojson(yelp_item: dict) -> dict:

    # create the GeoJSON Point
    pt = {
        "type": "Point",
        "coordinates": [
            yelp_item.get('coordinates').get('longitude'),
            yelp_item.get('coordinates').get('latitude')
        ]
    }

    # add the geojson to the Yelp item
    yelp_item['geojson'] = pt

    return yelp_item


def prep_yelp_item_for_arcgis(yelp_item: dict) -> dict:

    # get a string formatted address for display
    loc = yelp_item.get('location')
    if loc is not None:
        yelp_item['address'] = ', '.join(loc.get('display_address'))

    # get string formatted categories for display
    cats = yelp_item.get('categories')
    if cats is not None:
        cats = [cat.get('title') for cat in cats]
        cats.sort()
        yelp_item['categories'] = ', '.join(cats)

    # prune the dictionary
    keep_keys = ['id', 'name', 'image_url', 'url', 'review_count', 'categories', 'rating', 'price', 'address']
    keep_keys = [k for k in yelp_lst[0].keys() if k in keep_keys or k.startswith('h3_') or k == 'geometry']
    yelp_item = dict((k, yelp_item.get(k)) for k in keep_keys)

    return yelp_item


class Yelp(Session):

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {yelp_api_key}'
    }

    def get_businesses(
        self, 
        x: float = -122.91479355798339, 
        y: float = 47.042924037902935, 
        radius: int = 1600, 
        term: str = 'resaurants', 
        limit: int = 50, 
        sort_by: str = 'best_match', 
        raise_exception: bool = False
    ) -> List[dict]:
        
        # url for accessing the Yelp API
        yelp_business_search_url = 'https://api.yelp.com/v3/businesses/search'

        # populate the payload for the Yelp API request
        params = {
            'limit': limit,
            'sort_by': sort_by,
            'radius': radius,  # straight-line distance in meters
            'longitude': x,
            'latitude': y,
            'term': term
        } 

        # make the request to the Yelp API
        res = self.get(yelp_business_search_url, params=params)

        # if everything working just as expected
        if res.status_code == 200:
            
            # get the list of businesses from the response
            yelp_lst = res.json().get('businesses')
            
            # add the level h3 level 7 through 11 indices
            for h3_lvl in range(7, 12):
                yelp_lst = [add_h3_index(yelp_itm, h3_lvl) for yelp_itm in yelp_lst]

            # add GeoJSON geometry
            yelp_lst = [add_geojson(yelp_itm) for yelp_itm in yelp_lst]

        # if received an error and stopping execution is desired
        elif raise_exception:
            raise RequestException(f'Received a {res.status_code} status code response.\n{res.text}')
        
        # if wanting to continue execution even if error
        else:
            logging.warning(f'Received a {res.status_code} status code response.\n{res.text}')

            # create a list so no matter what, a list is returned
            yelp_lst = []

        return yelp_lst
