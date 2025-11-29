import bcrypt
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
        """Crea usuario cifrando automáticamente la contraseña"""
        # ✅ CIFRAR CONTRASEÑA AL REGISTRAR
        if 'password' in user_data:
            user_data['password'] = self._hash_password(user_data['password'])
            print(f"🔐 Contraseña cifrada para nuevo usuario: {user_data['email']}")
        
        return self.users.insert_one(user_data)
    
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
                # Actualizamos el usuario en memoria
                user['password'] = hashed_password
        
        return user
    
    def find_by_phone(self, phone):
        return self.users.find_one({"phone": phone})
    
    def user_exists(self, email):
        return self.users.find_one({"email": email}) is not None
    
    def update_user(self, email, update_data):
        """Actualiza usuario, cifrando automáticamente la contraseña si está presente"""
        # ✅ CIFRAR CONTRASEÑA SI SE ACTUALIZA
        if 'password' in update_data:
            update_data['password'] = self._hash_password(update_data['password'])
            print(f"🔐 Contraseña cifrada en actualización para: {email}")
        
        return self.users.update_one(
            {"email": email},
            {"$set": update_data}
        )
    
    def verify_password_for_login(self, email, plain_password):
        """Método especial para verificar contraseñas en el login SIN afectar main.py"""
        user = self.find_by_email(email)
        if not user or 'password' not in user:
            return False
        
        hashed_password = user['password']
        
        # Si es un hash bcrypt
        if hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
            return self._check_password(plain_password, hashed_password)
        else:
            # Si es texto plano (compatibilidad)
            return plain_password == hashed_password