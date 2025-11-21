from shared.database.mongo_connection import MongoDB

class UserRepository:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.users = self.db.users
    
    def create_user(self, user_data):
        return self.users.insert_one(user_data)
    
    def find_by_email(self, email):
        return self.users.find_one({"email": email})
    
    def find_by_phone(self, phone):
        return self.users.find_one({"phone": phone})
    
    def user_exists(self, email):
        return self.users.find_one({"email": email}) is not None
    
    def update_user(self, email, update_data):
        return self.users.update_one(
            {"email": email},
            {"$set": update_data}
        )