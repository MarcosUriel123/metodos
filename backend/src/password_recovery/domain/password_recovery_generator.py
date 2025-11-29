import random
import string
from datetime import datetime, timedelta

class PasswordRecoveryGenerator:
    """
    Generador para recuperación de contraseña
    """
    
    @staticmethod
    def generate_otp(length=6):
        """
        Genera un código OTP numérico
        """
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])
    
    @staticmethod
    def generate_expiration_time(minutes=10):
        """
        Genera tiempo de expiración
        """
        return datetime.now() + timedelta(minutes=minutes)
    
    @staticmethod
    def is_otp_expired(expires_at):
        """
        Verifica si un OTP ha expirado
        """
        return datetime.now() > expires_at
    
    @staticmethod
    def generate_recovery_token():
        """
        Genera un token de recuperación único
        """
        timestamp = str(int(datetime.now().timestamp()))
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return f"rec_{timestamp}_{random_chars}"
    
    @staticmethod
    def validate_password_strength(password):
        """
        Valida la fortaleza de la contraseña
        """
        if len(password) != 10:
            return False, "La contraseña debe tener exactamente 10 caracteres"
        
        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una mayúscula"
        
        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una minúscula"
        
        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un número"
        
        # Verificar que no contenga símbolos especiales
        if not all(c.isalnum() for c in password):
            return False, "La contraseña no puede contener símbolos especiales"
        
        return True, "Contraseña válida"