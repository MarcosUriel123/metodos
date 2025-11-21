import random
import string
from datetime import datetime, timedelta

class EmailOTPGenerator:
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Genera un código OTP numérico"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def get_expiration_time(minutes: int = 10) -> datetime:
        """Obtiene la fecha de expiración"""
        return datetime.now() + timedelta(minutes=minutes)
    
    @staticmethod
    def is_otp_expired(expires_at: datetime) -> bool:
        """Verifica si un OTP ha expirado"""
        return datetime.now() > expires_at