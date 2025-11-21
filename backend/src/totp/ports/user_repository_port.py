from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    @abstractmethod
    def save_user(self, email, secret, password, first_name, auth_method="totp"):
        pass
    
    @abstractmethod
    def get_secret_by_email(self, email):
        pass
    
    @abstractmethod
    def find_user_by_email(self, email):
        pass