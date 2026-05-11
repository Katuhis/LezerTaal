from pymongo import MongoClient
from config import MONGODB_URL

client = MongoClient(MONGODB_URL)
db = client['LezerTaal']

texts_collection = db['texts']
users_collection = db['users']
sections_collection = db['sections']