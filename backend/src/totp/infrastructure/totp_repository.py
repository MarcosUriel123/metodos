import bcrypt
from shared.database.mongo_connection import MongoDB
from ..ports.user_repository_port import UserRepositoryPort

class TOTPRepository(UserRepositoryPort):
    def __init__(self):
        self.db = MongoDB.get_db()
        self.users = self.db.users
    
    def _hash_password(self, password):
        """Cifra la contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    
    def save_user(self, email, secret, password, first_name, auth_method="totp"):
        # ✅ CIFRAR CONTRASEÑA ANTES DE GUARDAR
        hashed_password = self._hash_password(password)
        
        print(f"🔐 TOTP - Contraseña cifrada para: {email}")
        
        return self.users.insert_one({
            "email": email,
            "password": hashed_password,  # ✅ CONTRASEÑA CIFRADA
            "first_name": first_name,
            "secret": secret,
            "auth_method": auth_method,
            "phone_number": None
        })
    
    def get_secret_by_email(self, email):
        user = self.users.find_one({"email": email})
        return user.get("secret") if user else None
    
    def find_user_by_email(self, email):
        user = self.users.find_one({"email": email})
        
        # ✅ MIGRACIÓN AUTOMÁTICA (igual que UserRepository)
        if user and 'password' in user:
            current_password = user['password']
            if not current_password.startswith('$2'):
                print(f"🔄 TOTP - Migrando contraseña a bcrypt para: {email}")
                hashed_password = self._hash_password(current_password)
                self.users.update_one(
                    {"email": email},
                    {"$set": {"password": hashed_password}}
                )
                user['password'] = hashed_password
        
        return user
    
    def update_user_secret(self, email, secret):
        return self.users.update_one(
            {"email": email},
            {"$set": {"secret": secret}}
        )