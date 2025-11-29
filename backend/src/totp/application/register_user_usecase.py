from ..domain.totp_generator import TOTPGenerator

class RegisterUserUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, email, password, first_name, issuer_name="Mi App"):
        totp = TOTPGenerator(secret=None)
        secret = totp.generate_secret()
        uri = totp.generate_uri(email, issuer_name)
        
        print(f"📝 Registro TOTP iniciado para: {email}")
        self.user_repository.save_user(email, secret, password, first_name)
        print(f"✅ Usuario TOTP registrado con contraseña cifrada: {email}")
        
        return uri