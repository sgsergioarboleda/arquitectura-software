from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["Cluster0"]  
users_collection = db["Usuarios"]