from shared.database.mongo_connection import MongoDB
from ..ports.user_repository_port import UserRepositoryPort

class TOTPRepository(UserRepositoryPort):
    def __init__(self):
        self.db = MongoDB.get_db()
        self.users = self.db.users
    
    def save_user(self, email, secret, password, first_name, auth_method="totp"):
        return self.users.insert_one({
            "email": email,
            "password": password,
            "first_name": first_name,
            "secret": secret,
            "auth_method": auth_method,
            "phone_number": None
        })
    
    def get_secret_by_email(self, email):
        user = self.users.find_one({"email": email})
        return user.get("secret") if user else None
    
    def find_user_by_email(self, email):
        return self.users.find_one({"email": email})
    
    def update_user_secret(self, email, secret):
        return self.users.update_one(
            {"email": email},
            {"$set": {"secret": secret}}
        )