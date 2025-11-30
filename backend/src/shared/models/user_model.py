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
        Sanitización MEJORADA con protección completa
        - Detecta javascript: y otros patrones peligrosos
        - Bloquea palabras peligrosas completas
        - Escapa caracteres HTML
        """
        if not text:
            return text
        
        print(f"🧹 ANTES de sanitizar: '{text}'")
        
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
                print(f"🚫 PATRÓN PELIGROSO DETECTADO: {pattern}")
                print(f"🚫 Input rechazado completamente")
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
        except Exception as e:
            print(f"🚫 Error verificando contraseña: {e}")
            return False
    
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
    
    def create_user(self, user_data):
        """Crea usuario SANITIZANDO y cifrando automáticamente - SOLO CAMPOS DEL FORMULARIO"""
        print("=" * 60)
        print("🔐 CREATE_USER - Inicio (MEJORADO)")
        print(f"   Email: {user_data.get('email')}")
        print(f"   First Name (ORIGINAL): {user_data.get('first_name')}")
        print(f"   Last Name (ORIGINAL): {user_data.get('last_name')}")
        print("=" * 60)
        
        # ✅ VALIDAR EMAIL
        email = user_data.get('email')
        if not self._validate_email(email):
            print(f"🚫 Email inválido: {email}")
            raise ValueError("Formato de email inválido")
        
        # ✅ SANITIZAR SOLO LOS CAMPOS DEL FORMULARIO
        if 'first_name' in user_data:
            original = user_data['first_name']
            user_data['first_name'] = self._sanitize_input(user_data['first_name'])
            print(f"✅ First Name: '{original}' → '{user_data['first_name']}'")
        
        if 'last_name' in user_data:
            original = user_data['last_name']
            user_data['last_name'] = self._sanitize_input(user_data['last_name'])
            print(f"✅ Last Name: '{original}' → '{user_data['last_name']}'")
        
        # ✅ VALIDAR Y CIFRAR CONTRASEÑA
        if 'password' in user_data:
            password = user_data['password']
            
            # Validar fortaleza de contraseña
            is_valid, message = self._validate_password_strength(password)
            if not is_valid:
                print(f"🚫 Contraseña débil: {message}")
                raise ValueError(message)
            
            original_password = password
            user_data['password'] = self._hash_password(password)
            print(f"🔐 Contraseña cifrada para: {user_data['email']}")
            print(f"   Original: {original_password[:3]}...")
            print(f"   Hash: {user_data['password'][:20]}...")
        
        # ✅ VERIFICAR QUE EL USUARIO NO EXISTA
        if self.users.find_one({"email": email}):
            print(f"🚫 Usuario ya existe: {email}")
            raise ValueError("El usuario ya existe")
        
        # ✅ AGREGAR METADATOS BÁSICOS
        user_data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True
        })
        
        print("=" * 60)
        print("💾 Guardando en MongoDB...")
        
        result = self.users.insert_one(user_data)
        
        print(f"✅ Usuario creado con ID: {result.inserted_id}")
        print("=" * 60)
        
        return result
    
    def find_by_email(self, email):
        # ✅ VALIDAR EMAIL
        if not self._validate_email(email):
            return None
            
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
                    {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
                )
                user['password'] = hashed_password
        
        return user
    
    def find_by_phone(self, phone):
        return self.users.find_one({"phone_number": phone})
    
    def user_exists(self, email):
        # ✅ VALIDAR EMAIL
        if not self._validate_email(email):
            return False
            
        return self.users.find_one({"email": email}) is not None
    
    def update_user(self, email, update_data):
        """Actualiza usuario, SANITIZANDO y cifrando automáticamente"""
        print("=" * 60)
        print("🔄 UPDATE_USER - Inicio")
        print(f"   Email: {email}")
        print("=" * 60)
        
        # ✅ VALIDAR EMAIL
        if not self._validate_email(email):
            raise ValueError("Email inválido")
        
        # ✅ SANITIZAR CAMPOS DE TEXTO
        if 'first_name' in update_data:
            original = update_data['first_name']
            update_data['first_name'] = self._sanitize_input(update_data['first_name'])
            print(f"✅ First Name: '{original}' → '{update_data['first_name']}'")
        
        if 'last_name' in update_data:
            original = update_data['last_name']
            update_data['last_name'] = self._sanitize_input(update_data['last_name'])
            print(f"✅ Last Name: '{original}' → '{update_data['last_name']}'")
        
        # ✅ VALIDAR Y CIFRAR CONTRASEÑA SI SE ACTUALIZA
        if 'password' in update_data:
            password = update_data['password']
            
            # Validar fortaleza de contraseña
            is_valid, message = self._validate_password_strength(password)
            if not is_valid:
                print(f"🚫 Contraseña débil: {message}")
                raise ValueError(message)
            
            original_password = password
            update_data['password'] = self._hash_password(password)
            print(f"🔐 Contraseña cifrada en actualización")
        
        # ✅ ACTUALIZAR TIMESTAMP
        update_data['updated_at'] = datetime.utcnow()
        
        print("=" * 60)
        
        return self.users.update_one(
            {"email": email},
            {"$set": update_data}
        )
    
    def verify_password_for_login(self, email, plain_password):
        """Método especial para verificar contraseñas en el login"""
        # ✅ VALIDAR EMAIL
        if not self._validate_email(email):
            return False
            
        user = self.find_by_email(email)
        if not user or 'password' not in user:
            return False
        
        hashed_password = user['password']
        
        # ✅ Solo bcrypt, sin compatibilidad con texto plano
        if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
            return self._check_password(plain_password, hashed_password)
        else:
            # ❌ Texto plano no permitido en login
            print(f"🚫 Contraseña en texto plano detectada para: {email}")
            return False
    
    def verify_password_strength(self, password):
        """Método público para verificar fortaleza de contraseña"""
        return self._validate_password_strength(password)