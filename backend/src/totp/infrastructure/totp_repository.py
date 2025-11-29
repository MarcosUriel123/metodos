import bcrypt
import html
import re
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
    
    def _sanitize_input(self, text):
        """Sanitiza input para prevenir XSS - SIN RE-SANITIZACIÓN"""
        if not text:
            return text
        
        # ✅ REEMPLAZO SIMULTÁNEO (evita bucles)
        patterns_to_replace = {
            r'\bscript\b': '***',
            r'\bjavascript\b': '***', 
            r'\balert\b': '***',
            r'\beval\b': '***',
            r'\bonload\b': '***',
            r'\bonerror\b': '***',
            r'\bonclick\b': '***'
        }
        
        for pattern, replacement in patterns_to_replace.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # ✅ ESCAPAR CARACTERES HTML
        sanitized_text = html.escape(text).strip()
        
        return sanitized_text
    
    def save_user(self, email, secret, password, first_name, auth_method="totp"):
        # ✅ SANITIZAR first_name
        sanitized_first_name = self._sanitize_input(first_name)
        
        # ✅ CIFRAR CONTRASEÑA ANTES DE GUARDAR
        hashed_password = self._hash_password(password)
        
        print(f"🔐 TOTP - Usuario sanitizado: {sanitized_first_name}")
        
        return self.users.insert_one({
            "email": email,
            "password": hashed_password,  # ✅ CONTRASEÑA CIFRADA
            "first_name": sanitized_first_name,  # ✅ NOMBRE SANITIZADO
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