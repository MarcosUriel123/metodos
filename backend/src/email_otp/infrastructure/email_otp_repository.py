import random
import string
from datetime import datetime, timedelta
from shared.database.mongo_connection import MongoDB  # ✅ IMPORTAR LA CLASE

class EmailOTPRepository:
    def __init__(self):
        self.db = MongoDB.get_db()  # ✅ USAR EL MÉTODO ESTÁTICO
        self.collection = self.db.email_otps
    
    def generate_otp(self, email: str) -> str:
        """Genera un código OTP de 6 dígitos"""
        otp = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.now() + timedelta(minutes=10)
        
        # Guardar OTP en la base de datos
        self.collection.update_one(
            {'email': email},
            {
                '$set': {
                    'otp': otp,
                    'expires_at': expires_at,
                    'created_at': datetime.now(),
                    'attempts': 0
                }
            },
            upsert=True
        )
        
        return otp
    
    def verify_otp(self, email: str, otp: str) -> bool:
        """Verifica un código OTP"""
        record = self.collection.find_one({'email': email})
        
        if not record:
            return False
        
        # Verificar si el OTP ha expirado
        if datetime.now() > record['expires_at']:
            self.collection.delete_one({'email': email})
            return False
        
        # Verificar si el OTP coincide
        if record['otp'] == otp:
            self.collection.delete_one({'email': email})
            return True
        
        # Incrementar intentos fallidos
        self.collection.update_one(
            {'email': email},
            {'$inc': {'attempts': 1}}
        )
        
        return False
    
    def get_otp_info(self, email: str) -> dict:
        """Obtiene información del OTP actual"""
        record = self.collection.find_one({'email': email})
        if record:
            return {
                'email': record['email'],
                'expires_at': record['expires_at'],
                'attempts': record.get('attempts', 0),
                'created_at': record['created_at']
            }
        return None