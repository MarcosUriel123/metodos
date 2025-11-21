from pymongo import MongoClient
import os

class MongoDB:
    _instance = None
    
    def __init__(self):
        if MongoDB._instance is None:
            self.client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/metodos"))
            self.db = self.client["metodos"]  
            MongoDB._instance = self
    
    @staticmethod
    def get_db():
        if MongoDB._instance is None:
            MongoDB()
        return MongoDB._instance.db