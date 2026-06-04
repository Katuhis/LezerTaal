from pymongo import AsyncMongoClient, server_api
from pymongo.server_api import ServerApi
from config import MONGODB_URL

client = AsyncMongoClient(MONGODB_URL, server_api=ServerApi('1'))
db = client['LezerTaal']

texts_collection = db['texts']
users_collection = db['users']
sections_collection = db['sections']