from ..infrastructure.email_otp_repository import EmailOTPRepository
from ..infrastructure.brevo_email_adapter import BrevoEmailAdapter

class EmailOTPUseCases:
    def __init__(self):
        self.otp_repository = EmailOTPRepository()
        self.email_service = BrevoEmailAdapter()
    
    def send_otp(self, email: str) -> dict:
        """Envía un código OTP por email"""
        try:
            # Generar OTP
            otp_code = self.otp_repository.generate_otp(email)
            print(f"📧 Generado OTP para {email}: {otp_code}")
            
            # Enviar email
            success = self.email_service.send_otp_email(email, otp_code)
            
            if success:
                return {
                    'success': True,
                    'message': 'OTP sent successfully',
                    'email': email
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to send OTP email',
                    'email': email
                }
                
        except Exception as e:
            print(f"❌ Error in send_otp: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'email': email
            }
    
    def verify_otp(self, email: str, otp: str) -> dict:
        """Verifica un código OTP"""
        try:
            is_valid = self.otp_repository.verify_otp(email, otp)
            
            if is_valid:
                return {
                    'success': True,
                    'message': 'OTP verified successfully',
                    'email': email
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid or expired OTP',
                    'email': email
                }
                
        except Exception as e:
            print(f"❌ Error in verify_otp: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'email': email
            }