import bcrypt
import html
import re
from datetime import datetime
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
        Sanitización MEJORADA con protección completa
        - Detecta javascript: y otros patrones peligrosos
        - Bloquea palabras peligrosas completas
        - Escapa caracteres HTML
        """
        if not text:
            return text
        
        print(f"🧹 TOTP - ANTES de sanitizar: '{text}'")
        
        # ✅ PASO 1: Detectar patrones peligrosos CRÍTICOS ANTES de procesar
        critical_patterns = [
            r'javascript\s*:',  # ¡CRÍTICO! Bloquea javascript:
            r'data\s*:',        # Bloquea data URLs
            r'vbscript\s*:',    # Bloquea VBScript
            r'on\w+\s*=',       # Bloquea event handlers
            r'eval\s*\(',       # Bloquea eval(
            r'<script',         # Bloquea script tags
            r'<iframe',         # Bloquea iframes
            # Patrones sospechosos múltiples
            r'(script|javascript|alert|eval|onload|onerror|onclick|oninput){2,}'
        ]
        
        text_lower = text.lower()
        for pattern in critical_patterns:
            if re.search(pattern, text_lower, flags=re.IGNORECASE):
                print(f"🚫 TOTP - PATRÓN PELIGROSO DETECTADO: {pattern}")
                print(f"🚫 TOTP - Input rechazado completamente")
                return "***BLOCKED***"
        
        # ✅ PASO 2: Escapar caracteres HTML
        text = html.escape(text)
        
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
    
    def _validate_email(self, email):
        """Valida formato de email"""
        if not email or not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def _validate_password_strength(self, password):
        """Valida que la contraseña cumpla con los requisitos: 10 caracteres, 1 mayúscula, 1 minúscula, 1 número"""
        if len(password) < 10:
            return False, "La contraseña debe tener al menos 10 caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe tener al menos 1 mayúscula"
        
        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe tener al menos 1 minúscula"
        
        if not re.search(r'[0-9]', password):
            return False, "La contraseña debe tener al menos 1 número"
        
        return True, "Contraseña válida"
    
    def save_user(self, email, secret, password, first_name, auth_method="totp"):
        print("=" * 60)
        print("🔐 TOTP REPOSITORY - SAVE_USER (MEJORADO)")
        print(f"   Email: {email}")
        print(f"   First Name (ORIGINAL): {first_name}")
        print("=" * 60)
        
        # ✅ VALIDAR EMAIL
        if not self._validate_email(email):
            print(f"🚫 TOTP - Email inválido: {email}")
            raise ValueError("Formato de email inválido")
        
        # ✅ SANITIZAR first_name
        sanitized_first_name = self._sanitize_input(first_name)
        
        # ✅ VALIDAR CONTRASEÑA
        if not password:
            print(f"🚫 TOTP - Contraseña requerida")
            raise ValueError("La contraseña es requerida")
        
        # Validar fortaleza de contraseña
        is_valid, message = self._validate_password_strength(password)
        if not is_valid:
            print(f"🚫 TOTP - Contraseña débil: {message}")
            raise ValueError(message)
        
        # ✅ CIFRAR CONTRASEÑA ANTES DE GUARDAR
        hashed_password = self._hash_password(password)
        
        print(f"✅ First Name sanitizado: '{first_name}' → '{sanitized_first_name}'")
        print(f"🔐 Contraseña cifrada: {password[:3]}... → {hashed_password[:20]}...")
        print("=" * 60)
        
        # ✅ VERIFICAR QUE EL USUARIO NO EXISTA
        if self.users.find_one({"email": email}):
            print(f"🚫 TOTP - Usuario ya existe: {email}")
            raise ValueError("El usuario ya existe")
        
        result = self.users.insert_one({
            "email": email,
            "password": hashed_password,
            "first_name": sanitized_first_name,
            "secret": secret,
            "auth_method": auth_method,
            "phone_number": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        print(f"✅ TOTP User creado con ID: {result.inserted_id}")
        print("=" * 60)
        
        return result
    
    def get_secret_by_email(self, email):
        # ✅ VALIDAR EMAIL ANTES DE CONSULTAR
        if not self._validate_email(email):
            return None
            
        user = self.users.find_one({"email": email})
        return user.get("secret") if user else None
    
    def find_user_by_email(self, email):
        # ✅ VALIDAR EMAIL
        if not self._validate_email(email):
            return None
            
        user = self.users.find_one({"email": email})
        
        # ✅ MIGRACIÓN AUTOMÁTICA
        if user and 'password' in user:
            current_password = user['password']
            if not current_password.startswith('$2'):
                print(f"🔄 TOTP - Migrando contraseña a bcrypt para: {email}")
                hashed_password = self._hash_password(current_password)
                self.users.update_one(
                    {"email": email},
                    {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
                )
                user['password'] = hashed_password
        
        return user
    
    def update_user_secret(self, email, secret):
        # ✅ VALIDAR EMAIL
        if not self._validate_email(email):
            return None
            
        return self.users.update_one(
            {"email": email},
            {"$set": {"secret": secret, "updated_at": datetime.utcnow()}}
        )
    
    def verify_user_credentials(self, email, password):
        """Verifica credenciales de usuario de forma segura"""
        if not email or not password:
            return False
            
        user = self.find_user_by_email(email)
        if not user:
            return False
        
        stored_password = user.get('password')
        if not stored_password:
            return False
        
        # ✅ VERIFICAR CON BCRYPT
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                stored_password.encode('utf-8')
            )
        except Exception as e:
            print(f"🚫 TOTP - Error verificando contraseña: {e}")
            return False