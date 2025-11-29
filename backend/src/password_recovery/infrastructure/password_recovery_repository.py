from datetime import datetime
import bcrypt
from ...shared.database.mongo_connection import MongoDB

class PasswordRecoveryRepository:
    def __init__(self, db):
        self.db = db
        self.users_collection = self.db['users']
        self.password_recovery_collection = self.db['password_recovery']
    
    def find_user_by_email(self, email):
        """
        Busca un usuario por email
        """
        try:
            user = self.users_collection.find_one({'email': email})
            if user:
                print(f"✅ Usuario encontrado: {email}")
                return user
            else:
                print(f"❌ Usuario no encontrado: {email}")
                return None
        except Exception as e:
            print(f"❌ Error buscando usuario: {str(e)}")
            return None
    
    def save_recovery_request(self, recovery_data):
        """
        Guarda una solicitud de recuperación de contraseña
        """
        try:
            # Eliminar solicitudes anteriores del mismo email
            self.password_recovery_collection.delete_many({
                'email': recovery_data['email'],
                'used': False
            })
            
            # Insertar nueva solicitud
            result = self.password_recovery_collection.insert_one(recovery_data)
            
            if result.inserted_id:
                print(f"✅ Solicitud de recuperación guardada para: {recovery_data['email']}")
                return True
            else:
                print(f"❌ Error guardando solicitud de recuperación para: {recovery_data['email']}")
                return False
                
        except Exception as e:
            print(f"❌ Error guardando solicitud de recuperación: {str(e)}")
            return False
    
    def find_active_recovery_request(self, email, otp):
        """
        Busca una solicitud de recuperación activa y no expirada
        """
        try:
            recovery_request = self.password_recovery_collection.find_one({
                'email': email,
                'otp': otp,
                'used': False,
                'expires_at': {'$gt': datetime.now()}  # No expirado
            })
            
            if recovery_request:
                print(f"✅ Solicitud de recuperación activa encontrada para: {email}")
                return recovery_request
            else:
                print(f"❌ No se encontró solicitud de recuperación activa para: {email}")
                return None
                
        except Exception as e:
            print(f"❌ Error buscando solicitud de recuperación: {str(e)}")
            return None
    
    def find_verified_recovery_request(self, email, otp):
        """
        Busca una solicitud de recuperación verificada
        """
        try:
            recovery_request = self.password_recovery_collection.find_one({
                'email': email,
                'otp': otp,
                'used': False,
                'expires_at': {'$gt': datetime.now()}  # No expirado
            })
            
            return recovery_request
                
        except Exception as e:
            print(f"❌ Error buscando solicitud verificada: {str(e)}")
            return None
    
    def mark_recovery_as_used(self, email, otp):
        """
        Marca una solicitud de recuperación como usada
        """
        try:
            result = self.password_recovery_collection.update_one(
                {
                    'email': email,
                    'otp': otp
                },
                {
                    '$set': {
                        'used': True,
                        'used_at': datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Solicitud de recuperación marcada como usada para: {email}")
                return True
            else:
                print(f"❌ Error marcando solicitud como usada para: {email}")
                return False
                
        except Exception as e:
            print(f"❌ Error marcando solicitud como usada: {str(e)}")
            return False
    
    def mark_recovery_as_verified(self, email, otp):
        """
        Marca una solicitud de recuperación como verificada
        """
        try:
            result = self.password_recovery_collection.update_one(
                {
                    'email': email,
                    'otp': otp
                },
                {
                    '$set': {
                        'verified': True,
                        'verified_at': datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Solicitud de recuperación verificada para: {email}")
                return True
            else:
                print(f"❌ Error verificando solicitud para: {email}")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando solicitud: {str(e)}")
            return False
    
    def update_user_password(self, email, new_password):
        """
        Actualiza la contraseña del usuario
        """
        try:
            # Encriptar la nueva contraseña
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            result = self.users_collection.update_one(
                {'email': email},
                {
                    '$set': {
                        'password': hashed_password,
                        'updated_at': datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Contraseña actualizada para: {email}")
                return True
            else:
                print(f"❌ Error actualizando contraseña para: {email}")
                return False
                
        except Exception as e:
            print(f"❌ Error actualizando contraseña: {str(e)}")
            return False
    
    def cleanup_expired_recovery_requests(self):
        """
        Limpia solicitudes de recuperación expiradas
        """
        try:
            result = self.password_recovery_collection.delete_many({
                'expires_at': {'$lt': datetime.now()}
            })
            
            print(f"🧹 Solicitudes de recuperación expiradas eliminadas: {result.deleted_count}")
            return result.deleted_count
            
        except Exception as e:
            print(f"❌ Error limpiando solicitudes expiradas: {str(e)}")
            return 0