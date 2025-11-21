from ..domain.totp_generator import TOTPGenerator

class GenerateQRUseCase:
    def __init__(self, qr_service):
        self.qr_service = qr_service

    def execute(self, secret, email, issuer):
        totp = TOTPGenerator(secret=secret)
        uri = totp.generate_uri(email, issuer)
        return self.qr_service.generate_qr_image(uri)