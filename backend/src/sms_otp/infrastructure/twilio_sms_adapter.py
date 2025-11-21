from twilio.rest import Client
import os
from ..ports.sms_service_port import SMSServicePort

class TwilioSMSAdapter(SMSServicePort):
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Missing Twilio credentials")
        
        self.client = Client(self.account_sid, self.auth_token)

    def send_otp(self, phone_number: str, otp: str) -> bool:
        try:
            message = self.client.messages.create(
                body=f'Tu código de verificación es: {otp}',
                from_=self.phone_number,
                to=phone_number
            )
            print(f"✅ SMS enviado a {phone_number}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error enviando SMS: {e}")
            return False