import random
import time
from datetime import datetime, timedelta

class RequestPasswordRecoveryUseCase:
    def __init__(self, password_recovery_repository, email_adapter):
        self.password_recovery_repo = password_recovery_repository
        self.email_adapter = email_adapter
    
    def execute(self, email):
        """
        Solicita recuperación de contraseña para un email
        """
        try:
            print(f"📧 Iniciando recuperación para: {email}")
            
            # 1. Verificar si el usuario existe
            user = self.password_recovery_repo.find_user_by_email(email)
            if not user:
                print(f"❌ Usuario no encontrado: {email}")
                return {
                    'success': False,
                    'error': 'No existe una cuenta con este correo electrónico'
                }
            
            # 2. Generar código OTP de 6 dígitos
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            expires_at = datetime.now() + timedelta(minutes=10)  # Expira en 10 minutos
            
            print(f"🔐 OTP generado para {email}: {otp}")
            
            # 3. Guardar solicitud de recuperación
            recovery_data = {
                'email': email,
                'otp': otp,
                'expires_at': expires_at,
                'used': False,
                'created_at': datetime.now()
            }
            
            save_result = self.password_recovery_repo.save_recovery_request(recovery_data)
            if not save_result:
                return {
                    'success': False,
                    'error': 'Error al guardar la solicitud de recuperación'
                }
            
            # 4. ✅ USAR EL MÉTODO EXISTENTE send_otp_email()
            print(f"📤 Enviando OTP de recuperación por email a: {email}")
            email_sent = self.email_adapter.send_otp_email(email, otp)
            
            if not email_sent:
                print(f"❌ Error al enviar email a: {email}")
                return {
                    'success': False,
                    'error': 'Error al enviar el código de verificación'
                }
            
            print(f"✅ Email de recuperación enviado a: {email}")
            
            return {
                'success': True,
                'recovery_token': f"temp_token_{int(time.time())}"  # Token temporal
            }
            
        except Exception as e:
            print(f"❌ Error en RequestPasswordRecoveryUseCase: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': 'Error interno del servidor'
            }

class VerifyRecoveryOTPUseCase:
    def __init__(self, password_recovery_repository):
        self.password_recovery_repo = password_recovery_repository
    
    def execute(self, email, otp):
        """
        Verifica el código OTP de recuperación
        """
        try:
            print(f"🔍 Verificando OTP para: {email}")
            
            # 1. Buscar solicitud de recuperación activa
            recovery_request = self.password_recovery_repo.find_active_recovery_request(email, otp)
            if not recovery_request:
                return {
                    'success': False,
                    'error': 'Código inválido o expirado'
                }
            
            # 2. Verificar si el código ha expirado
            if recovery_request['expires_at'] < datetime.now():
                # Marcar como expirado
                self.password_recovery_repo.mark_recovery_as_used(email, otp)
                return {
                    'success': False,
                    'error': 'El código ha expirado. Solicita uno nuevo.'
                }
            
            # 3. Marcar código como verificado (pero no usado aún)
            self.password_recovery_repo.mark_recovery_as_verified(email, otp)
            
            print(f"✅ OTP verificado correctamente para: {email}")
            
            return {
                'success': True,
                'recovery_token': f"verified_{int(time.time())}"
            }
            
        except Exception as e:
            print(f"❌ Error en VerifyRecoveryOTPUseCase: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': 'Error interno del servidor'
            }

class ResetPasswordUseCase:
    def __init__(self, password_recovery_repository, user_repository):
        self.password_recovery_repo = password_recovery_repository
        self.user_repo = user_repository  # ✅ AGREGAR UserRepository
    
    def execute(self, email, otp, new_password):
        """
        Restablece la contraseña del usuario
        """
        try:
            print(f"🔄 Restableciendo contraseña para: {email}")
            
            # 1. Verificar que la solicitud de recuperación sea válida
            recovery_request = self.password_recovery_repo.find_verified_recovery_request(email, otp)
            if not recovery_request:
                # Si no está verificada, buscar si es válida aunque no esté marcada como verificada
                recovery_request = self.password_recovery_repo.find_active_recovery_request(email, otp)
                if not recovery_request:
                    return {
                        'success': False,
                        'error': 'Solicitud de recuperación inválida o expirada'
                    }
            
            # 2. Verificar que el código no haya expirado
            if recovery_request['expires_at'] < datetime.now():
                self.password_recovery_repo.mark_recovery_as_used(email, otp)
                return {
                    'success': False,
                    'error': 'El código ha expirado. Solicita uno nuevo.'
                }
            
            # 3. ✅ ACTUALIZAR CONTRASEÑA USANDO user_repo.update_user()
            update_data = {"password": new_password}
            update_result = self.user_repo.update_user(email, update_data)
            
            if not update_result:
                return {
                    'success': False,
                    'error': 'Error al actualizar la contraseña'
                }
            
            # 4. Marcar solicitud de recuperación como usada
            self.password_recovery_repo.mark_recovery_as_used(email, otp)
            
            print(f"✅ Contraseña actualizada correctamente para: {email}")
            
            return {
                'success': True,
                'message': 'Contraseña actualizada correctamente'
            }
            
        except Exception as e:
            print(f"❌ Error en ResetPasswordUseCase: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': 'Error interno del servidor'
            }