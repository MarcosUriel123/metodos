import random
import time
from datetime import datetime, timedelta
from ..infrastructure.sms_otp_repository import SMSOTPRepository

class SMSOTPGenerator:
    def __init__(self, length: int = 6, expiry_minutes: int = 5):
        self.length = length
        self.expiry_minutes = expiry_minutes
        self.otp_repo = SMSOTPRepository()

    def generate_otp(self, phone_number: str) -> str:
        otp = ''.join([str(random.randint(0, 9)) for _ in range(self.length)])
        expiry_time = datetime.now() + timedelta(minutes=self.expiry_minutes)
        
        self.otp_repo.save_otp(phone_number, otp, expiry_time)
        print(f"🔐 OTP generado para {phone_number}: {otp}")
        return otp

    def verify_otp(self, phone_number: str, otp: str) -> bool:
        otp_record = self.otp_repo.find_valid_otp(phone_number)
        
        if not otp_record:
            print(f"❌ No hay OTP válido para {phone_number}")
            return False
        
        if otp_record['code'] == otp:
            self.otp_repo.mark_otp_used(phone_number)
            print(f"✅ OTP válido para {phone_number}")
            return True
        
        print(f"❌ OTP incorrecto para {phone_number}")
        return False