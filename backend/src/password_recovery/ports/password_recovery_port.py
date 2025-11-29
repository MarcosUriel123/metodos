from abc import ABC, abstractmethod
from datetime import datetime

class PasswordRecoveryRepositoryPort(ABC):
    """
    Puerto para el repositorio de recuperación de contraseña
    """
    
    @abstractmethod
    def find_user_by_email(self, email):
        """Busca un usuario por email"""
        pass
    
    @abstractmethod
    def save_recovery_request(self, recovery_data):
        """Guarda una solicitud de recuperación"""
        pass
    
    @abstractmethod
    def find_active_recovery_request(self, email, otp):
        """Busca solicitud activa no expirada"""
        pass
    
    @abstractmethod
    def find_verified_recovery_request(self, email, otp):
        """Busca solicitud verificada"""
        pass
    
    @abstractmethod
    def mark_recovery_as_used(self, email, otp):
        """Marca solicitud como usada"""
        pass
    
    @abstractmethod
    def mark_recovery_as_verified(self, email, otp):
        """Marca solicitud como verificada"""
        pass
    
    @abstractmethod
    def update_user_password(self, email, new_password):
        """Actualiza contraseña del usuario"""
        pass

class EmailServicePort(ABC):
    """
    Puerto para el servicio de email
    """
    
    @abstractmethod
    def send_email(self, to_email, subject, html_content):
        """Envía un email"""
        pass