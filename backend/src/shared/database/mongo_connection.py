from pymongo import MongoClient
import os

class MongoDB:
    _instance = None
    
    def __init__(self):
        if MongoDB._instance is None:
            # Usar la variable de entorno de Render
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/metodos")
            print(f"🔗 Conectando a MongoDB: {mongo_uri}")
            
            self.client = MongoClient(mongo_uri)
            self.db = self.client["metodos"]  
            MongoDB._instance = self
            
            # Verificar conexión
            try:
                self.client.admin.command('ping')
                print("✅ Conexión a MongoDB exitosa")
            except Exception as e:
                print(f"❌ Error conectando a MongoDB: {e}")
    
    @staticmethod
    def get_db():
        if MongoDB._instance is None:
            MongoDB()
        return MongoDB._instance.db