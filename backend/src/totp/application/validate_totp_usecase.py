from ..domain.totp_generator import TOTPGenerator

class ValidateTOTPUseCase:
    def __init__(self, secret):
        self.secret = secret

    def execute(self, code: str) -> bool:
        totp = TOTPGenerator(secret=self.secret)
        return totp.verify_code(code)