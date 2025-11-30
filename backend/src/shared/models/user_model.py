import bcrypt
import html
import re
from datetime import datetime
from shared.database.mongo_connection import MongoDB

class UserRepository:
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
        Sanitiza input para prevenir XSS - MANTENIENDO TU LÓGICA ORIGINAL
        """
        if not text:
            return text
        
        print(f"🧹 ANTES de sanitizar: '{text}'")
        
        # ✅ DETECCIÓN DE javascript: ANTES de escapar (MEJORA CRÍTICA)
        critical_patterns = [
            r'javascript\s*:',  # ¡ESTO FALTABA! Bloquea javascript:
            r'data\s*:',        # Bloquea data URLs
            r'vbscript\s*:',    # Bloquea VBScript
            r'on\w+\s*=',       # Bloquea event handlers
        ]
        
        text_lower = text.lower()
        for pattern in critical_patterns:
            if re.search(pattern, text_lower, flags=re.IGNORECASE):
                print(f"🚫 PATRÓN PELIGROSO DETECTADO: {pattern}")
                return "***BLOCKED***"
        
        # ✅ TU LÓGICA ORIGINAL (SE MANTIENE IGUAL)
        # PASO 1: Escapar caracteres HTML primero
        text = html.escape(text)
        
        # PASO 2: Detectar patrones sospechosos 
        suspicious_pattern = r'(script|javascript|alert|eval|onload|onerror|onclick|oninput){2,}'
        if re.search(suspicious_pattern, text, flags=re.IGNORECASE):
            print(f"⚠️ PATRÓN SOSPECHOSO DETECTADO: Múltiples palabras peligrosas juntas")
            return "***BLOCKED***"
        
        # PASO 3: Bloquear palabras peligrosas completas (con word boundaries)
        dangerous_words = [
            'script', 'javascript', 'alert', 'eval', 
            'onload', 'onerror', 'onclick', 'oninput', 'onmouseover',
            'onchange', 'onsubmit', 'onkeydown', 'onkeyup', 'onfocus',
            'onblur', 'onmouseout', 'onmousemove', 'onmouseenter',
            'onmouseleave', 'ondblclick', 'oncontextmenu'
        ]
        
        for word in dangerous_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            text = re.sub(pattern, '***', text, flags=re.IGNORECASE)
        
        text = text.strip()
        
        print(f"🧹 DESPUÉS de sanitizar: '{text}'")
        
        return text
    
    def _check_password(self, plain_password, hashed_password):
        """Verifica si la contraseña coincide con el hash"""
        if not hashed_password:
            return False
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def create_user(self, user_data):
        """Crea usuario SANITIZANDO y cifrando automáticamente"""
        print("=" * 60)
        print("🔐 CREATE_USER - Inicio")
        print(f"   Email: {user_data.get('email')}")
        print(f"   First Name (ORIGINAL): {user_data.get('first_name')}")
        print(f"   Last Name (ORIGINAL): {user_data.get('last_name')}")
        print("=" * 60)
        
        # ✅ SANITIZAR CAMPOS DE TEXTO (IGUAL QUE ANTES)
        if 'first_name' in user_data:
            original = user_data['first_name']
            user_data['first_name'] = self._sanitize_input(user_data['first_name'])
            print(f"✅ First Name: '{original}' → '{user_data['first_name']}'")
        
        if 'last_name' in user_data:
            original = user_data['last_name']
            user_data['last_name'] = self._sanitize_input(user_data['last_name'])
            print(f"✅ Last Name: '{original}' → '{user_data['last_name']}'")
        
        # ✅ CIFRAR CONTRASEÑA AL REGISTRAR (IGUAL QUE ANTES)
        if 'password' in user_data:
            original_password = user_data['password']
            user_data['password'] = self._hash_password(user_data['password'])
            print(f"🔐 Contraseña cifrada para: {user_data['email']}")
            print(f"   Original: {original_password[:3]}...")
            print(f"   Hash: {user_data['password'][:20]}...")
        
        # ✅ AGREGAR TIMESTAMP (MEJORA MINIMA)
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        
        print("=" * 60)
        print("💾 Guardando en MongoDB...")
        
        result = self.users.insert_one(user_data)
        
        print(f"✅ Usuario creado con ID: {result.inserted_id}")
        print("=" * 60)
        
        return result
    
    # 🔁 TODOS LOS DEMÁS MÉTODOS SE MANTIENEN EXACTAMENTE IGUAL
    def find_by_email(self, email):
        user = self.users.find_one({"email": email})
        
        if user and 'password' in user:
            current_password = user['password']
            if not current_password.startswith('$2'):
                print(f"🔄 Migrando contraseña a bcrypt para: {email}")
                hashed_password = self._hash_password(current_password)
                self.users.update_one(
                    {"email": email},
                    {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
                )
                user['password'] = hashed_password
        
        return user
    
    def find_by_phone(self, phone):
        return self.users.find_one({"phone_number": phone})
    
    def user_exists(self, email):
        return self.users.find_one({"email": email}) is not None
    
    def update_user(self, email, update_data):
        """Actualiza usuario, SANITIZANDO y cifrando automáticamente"""
        print("=" * 60)
        print("🔄 UPDATE_USER - Inicio")
        print(f"   Email: {email}")
        print("=" * 60)
        
        if 'first_name' in update_data:
            original = update_data['first_name']
            update_data['first_name'] = self._sanitize_input(update_data['first_name'])
            print(f"✅ First Name: '{original}' → '{update_data['first_name']}'")
        
        if 'last_name' in update_data:
            original = update_data['last_name']
            update_data['last_name'] = self._sanitize_input(update_data['last_name'])
            print(f"✅ Last Name: '{original}' → '{update_data['last_name']}'")
        
        if 'password' in update_data:
            original_password = update_data['password']
            update_data['password'] = self._hash_password(update_data['password'])
            print(f"🔐 Contraseña cifrada en actualización")
        
        update_data['updated_at'] = datetime.utcnow()
        
        print("=" * 60)
        
        return self.users.update_one(
            {"email": email},
            {"$set": update_data}
        )
    
    def verify_password_for_login(self, email, plain_password):
        """Método especial para verificar contraseñas en el login"""
        user = self.find_by_email(email)
        if not user or 'password' not in user:
            return False
        
        hashed_password = user['password']
        
        if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
            return self._check_password(plain_password, hashed_password)
        else:
            return plain_password == hashed_password