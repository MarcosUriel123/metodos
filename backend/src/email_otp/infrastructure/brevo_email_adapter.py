import os
import requests
from ..ports.email_service_port import EmailServicePort

class BrevoEmailAdapter(EmailServicePort):
    def __init__(self):
        self.api_key = os.getenv('BREVO_API_KEY')
        self.sender_email = os.getenv('BREVO_SENDER_EMAIL')
        self.sender_name = os.getenv('BREVO_SENDER_NAME')
        self.base_url = "https://api.brevo.com/v3/smtp/email"
    
    def send_otp_email(self, to_email: str, otp_code: str) -> bool:
        """
        Envía un código OTP por email usando Brevo API
        """
        payload = {
            "sender": {
                "name": self.sender_name,
                "email": self.sender_email
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_email.split('@')[0]
                }
            ],
            "subject": "Tu código de verificación SecureAuth",
            "htmlContent": self._generate_html_content(otp_code)
        }
        
        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }
        
        try:
            print(f"📧 Enviando email a: {to_email}")
            print(f"🔑 Usando API Key: {self.api_key[:6]}...")
            print(f"👤 Remitente: {self.sender_name} <{self.sender_email}>")
            
            response = requests.post(self.base_url, json=payload, headers=headers)
            
            print(f"📡 Respuesta Brevo - Status: {response.status_code}")
            if response.status_code != 201:
                print(f"❌ Error Brevo: {response.text}")
            
            return response.status_code == 201
            
        except Exception as e:
            print(f"🚨 Error enviando email: {e}")
            return False
    
    def _generate_html_content(self, otp_code: str) -> str:
        """
        Genera el contenido HTML del email
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                .code {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 32px; 
                        font-weight: bold; letter-spacing: 8px; margin: 30px 0; border-radius: 8px; }}
                .footer {{ margin-top: 30px; padding: 20px; background: #f9fafb; text-align: center; 
                         color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 SecureAuth</h1>
                    <p>Verificación de Seguridad</p>
                </div>
                
                <h2>Hola,</h2>
                <p>Tu código de verificación para acceder a SecureAuth es:</p>
                
                <div class="code">{otp_code}</div>
                
                <p>Este código es válido por <strong>tiempo limitado</strong>.</p>
                <p>Si no solicitaste este código, por favor ignora este mensaje.</p>
                
                <div class="footer">
                    <p>© 2024 SecureAuth. Todos los derechos reservados.</p>
                    <p>Este es un email automático, por favor no respondas.</p>
                </div>
            </div>
        </body>
        </html>
        """