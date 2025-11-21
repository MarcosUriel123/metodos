from shared.database.mongo_connection import MongoDB
from datetime import datetime 


class SMSOTPRepository:
    def __init__(self):
        self.db = MongoDB.get_db()
        self.otps = self.db.sms_otps
    
    def save_otp(self, phone, code, expires):
        return self.otps.update_one(
            {"phone": phone},
            {"$set": {
                "code": code, 
                "expires": expires,
                "used": False
            }},
            upsert=True
        )
    
    def find_valid_otp(self, phone):
        return self.otps.find_one({
            "phone": phone,
            "used": False,
            "expires": {"$gt": datetime.now()}
        })
    
    def mark_otp_used(self, phone):
        return self.otps.update_one(
            {"phone": phone},
            {"$set": {"used": True}}
        )