from flask import Blueprint, request, jsonify
from ....shared.database.mongo_connection import MongoDB
from ....shared.models.user_model import User
from ....email_otp.infrastructure.brevo_email_adapter import BrevoEmailAdapter
from ...application.password_recovery_usecases import (
    RequestPasswordRecoveryUseCase,
    VerifyRecoveryOTPUseCase,
    ResetPasswordUseCase
)
from ...infrastructure.password_recovery_repository import PasswordRecoveryRepository

# Configuración del Blueprint
password_recovery_bp = Blueprint('password_recovery', __name__)

# Inicializar dependencias
db = MongoDB.get_db()
password_recovery_repo = PasswordRecoveryRepository(db)
email_adapter = BrevoEmailAdapter()

# Casos de uso
request_recovery_uc = RequestPasswordRecoveryUseCase(password_recovery_repo, email_adapter)
verify_otp_uc = VerifyRecoveryOTPUseCase(password_recovery_repo)
reset_password_uc = ResetPasswordUseCase(password_recovery_repo)

@password_recovery_bp.route('/api/auth/password-recovery/request', methods=['POST'])
def request_password_recovery():
    """
    Endpoint para solicitar recuperación de contraseña
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'El email es requerido'
            }), 400
        
        print(f"🔐 Solicitud de recuperación para: {email}")
        
        # Ejecutar caso de uso
        result = request_recovery_uc.execute(email)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Código de recuperación enviado correctamente',
                'recovery_token': result.get('recovery_token')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        print(f"❌ Error en request_password_recovery: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@password_recovery_bp.route('/api/auth/password-recovery/verify-otp', methods=['POST'])
def verify_recovery_otp():
    """
    Endpoint para verificar el OTP de recuperación
    """
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({
                'success': False,
                'error': 'Email y código son requeridos'
            }), 400
        
        print(f"🔐 Verificación OTP para: {email}")
        
        # Ejecutar caso de uso
        result = verify_otp_uc.execute(email, otp)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Código verificado correctamente',
                'recovery_token': result.get('recovery_token')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        print(f"❌ Error en verify_recovery_otp: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@password_recovery_bp.route('/api/auth/password-recovery/reset', methods=['POST'])
def reset_password():
    """
    Endpoint para restablecer la contraseña
    """
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')
        new_password = data.get('new_password')
        
        if not email or not otp or not new_password:
            return jsonify({
                'success': False,
                'error': 'Email, código y nueva contraseña son requeridos'
            }), 400
        
        print(f"🔐 Restableciendo contraseña para: {email}")
        
        # Ejecutar caso de uso
        result = reset_password_uc.execute(email, otp, new_password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Contraseña actualizada correctamente'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        print(f"❌ Error en reset_password: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500