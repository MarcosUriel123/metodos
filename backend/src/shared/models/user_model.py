import bcrypt
import html
import re
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
        Sanitiza input para prevenir XSS
        - Bloquea palabras peligrosas completas (con word boundaries)
        - Detecta patrones sospechosos (múltiples palabras peligrosas juntas)
        - Escapa caracteres HTML
        """
        if not text:
            return text
        
        print(f"🧹 ANTES de sanitizar: '{text}'")
        
        # ✅ PASO 1: Escapar caracteres HTML primero
        text = html.escape(text)
        
        # ✅ PASO 2: Detectar patrones sospechosos ANTES de procesar
        # Si hay múltiples palabras peligrosas pegadas sin espacios
        suspicious_pattern = r'(script|javascript|alert|eval|onload|onerror|onclick|oninput){2,}'
        if re.search(suspicious_pattern, text, flags=re.IGNORECASE):
            print(f"⚠️ PATRÓN SOSPECHOSO DETECTADO: Múltiples palabras peligrosas juntas")
            print(f"🚫 Input rechazado completamente")
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
        
        # ✅ SANITIZAR CAMPOS DE TEXTO
        if 'first_name' in user_data:
            original = user_data['first_name']
            user_data['first_name'] = self._sanitize_input(user_data['first_name'])
            print(f"✅ First Name: '{original}' → '{user_data['first_name']}'")
        
        if 'last_name' in user_data:
            original = user_data['last_name']
            user_data['last_name'] = self._sanitize_input(user_data['last_name'])
            print(f"✅ Last Name: '{original}' → '{user_data['last_name']}'")
        
        # ✅ CIFRAR CONTRASEÑA AL REGISTRAR
        if 'password' in user_data:
            original_password = user_data['password']
            user_data['password'] = self._hash_password(user_data['password'])
            print(f"🔐 Contraseña cifrada para: {user_data['email']}")
            print(f"   Original: {original_password[:3]}...")
            print(f"   Hash: {user_data['password'][:20]}...")
        
        print("=" * 60)
        print("💾 Guardando en MongoDB...")
        
        result = self.users.insert_one(user_data)
        
        print(f"✅ Usuario creado con ID: {result.inserted_id}")
        print("=" * 60)
        
        return result
    
    def find_by_email(self, email):
        user = self.users.find_one({"email": email})
        
        # ✅ MIGRACIÓN AUTOMÁTICA: Si la contraseña está en texto plano, la ciframos
        if user and 'password' in user:
            current_password = user['password']
            # Si NO es un hash bcrypt (no empieza con $2), la ciframos
            if not current_password.startswith('$2'):
                print(f"🔄 Migrando contraseña a bcrypt para: {email}")
                hashed_password = self._hash_password(current_password)
                self.users.update_one(
                    {"email": email},
                    {"$set": {"password": hashed_password}}
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
        
        # ✅ SANITIZAR CAMPOS DE TEXTO
        if 'first_name' in update_data:
            original = update_data['first_name']
            update_data['first_name'] = self._sanitize_input(update_data['first_name'])
            print(f"✅ First Name: '{original}' → '{update_data['first_name']}'")
        
        if 'last_name' in update_data:
            original = update_data['last_name']
            update_data['last_name'] = self._sanitize_input(update_data['last_name'])
            print(f"✅ Last Name: '{original}' → '{update_data['last_name']}'")
        
        # ✅ CIFRAR CONTRASEÑA SI SE ACTUALIZA
        if 'password' in update_data:
            original_password = update_data['password']
            update_data['password'] = self._hash_password(update_data['password'])
            print(f"🔐 Contraseña cifrada en actualización")
        
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
        
        # Si es un hash bcrypt
        if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
            return self._check_password(plain_password, hashed_password)
        else:
            # Si es texto plano (compatibilidad temporal)
            return plain_password == hashed_password