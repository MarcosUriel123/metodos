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
        """
        Sanitiza input para prevenir XSS
        - Bloquea palabras peligrosas completas (con word boundaries)
        - Detecta patrones sospechosos (múltiples palabras peligrosas juntas)
        - Escapa caracteres HTML
        """
        if not text:
            return text
        
        print(f"🧹 TOTP - ANTES de sanitizar: '{text}'")
        
        # ✅ PASO 1: Escapar caracteres HTML primero
        text = html.escape(text)
        
        # ✅ PASO 2: Detectar patrones sospechosos ANTES de procesar
        # Si hay múltiples palabras peligrosas pegadas sin espacios
        suspicious_pattern = r'(script|javascript|alert|eval|onload|onerror|onclick|oninput){2,}'
        if re.search(suspicious_pattern, text, flags=re.IGNORECASE):
            print(f"⚠️ TOTP - PATRÓN SOSPECHOSO DETECTADO: Múltiples palabras peligrosas juntas")
            print(f"🚫 TOTP - Input rechazado completamente")
            return "***BLOCKED***"
        
        # ✅ PASO 3: Bloquear palabras peligrosas completas (con word boundaries)
        # Esto permite "prescription" pero bloquea "script"
        dangerous_words = [
            'script', 'javascript', 'alert', 'eval', 
            'onload', 'onerror', 'onclick', 'oninput', 'onmouseover',
            'onchange', 'onsubmit', 'onkeydown', 'onkeyup', 'onfocus',
            'onblur', 'onmouseout', 'onmousemove', 'onmouseenter',
            'onmouseleave', 'ondblclick', 'oncontextmenu'
        ]
        
        for word in dangerous_words:
            # \b = word boundary (inicio/fin de palabra)
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, '***', text, flags=re.IGNORECASE)
        
        text = text.strip()
        
        print(f"🧹 TOTP - DESPUÉS de sanitizar: '{text}'")
        
        return text
    
    def save_user(self, email, secret, password, first_name, auth_method="totp"):
        print("=" * 60)
        print("🔐 TOTP REPOSITORY - SAVE_USER")
        print(f"   Email: {email}")
        print(f"   First Name (ORIGINAL): {first_name}")
        print("=" * 60)
        
        # ✅ SANITIZAR first_name
        sanitized_first_name = self._sanitize_input(first_name)
        
        # ✅ CIFRAR CONTRASEÑA ANTES DE GUARDAR
        hashed_password = self._hash_password(password)
        
        print(f"✅ First Name sanitizado: '{first_name}' → '{sanitized_first_name}'")
        print(f"🔐 Contraseña cifrada: {password[:3]}... → {hashed_password[:20]}...")
        print("=" * 60)
        
        result = self.users.insert_one({
            "email": email,
            "password": hashed_password,
            "first_name": sanitized_first_name,
            "secret": secret,
            "auth_method": auth_method,
            "phone_number": None
        })
        
        print(f"✅ TOTP User creado con ID: {result.inserted_id}")
        print("=" * 60)
        
        return result
    
    def get_secret_by_email(self, email):
        user = self.users.find_one({"email": email})
        return user.get("secret") if user else None
    
    def find_user_by_email(self, email):
        user = self.users.find_one({"email": email})
        
        # ✅ MIGRACIÓN AUTOMÁTICA
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