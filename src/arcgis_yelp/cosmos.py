import os
from collections.abc import Generator
from typing import Optional

from arcgis.geometry import Polygon, Envelope
from azure.cosmos import CosmosClient, ContainerProxy
import h3

get_cosmos_container_client(cosmos_url: Optional[str] = None, cosmos_key: Optional[str] = None, cosmos_db: Optional[str] = None, cosmos_container)

cosmos_url = os.getenv('COSMOS_URL')
cosmos_key = os.getenv('COSMOS_KEY')
cosmos_db = os.getenv('COSMOS_DB')
cosmos_container = os.getenv('COSMOS_CONTAINER')

client = CosmosClient(url=cosmos_url, credential=cosmos_key)
db = client.get_database_client('Yelp')
container = db.get_container_client('Items')

container