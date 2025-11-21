from flask import Blueprint, request, jsonify, session, Response
from ...application.generate_qr_usecase import GenerateQRUseCase
from ...application.validate_totp_usecase import ValidateTOTPUseCase
from ...application.register_user_usecase import RegisterUserUseCase
from ...adapters.http.qr_generator_adapter import QRGeneratorAdapter
from ...infrastructure.totp_repository import TOTPRepository

totp_bp = Blueprint('totp', __name__)

# Inicializar dependencias
user_repo = TOTPRepository()
qr_adapter = QRGeneratorAdapter()
generate_qr_usecase = GenerateQRUseCase(qr_adapter)
register_usecase = RegisterUserUseCase(user_repo)

@totp_bp.route('/setup', methods=['POST'])
def setup_totp():
    """Configurar TOTP para un usuario existente"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Generar secreto y URI para TOTP
        uri = register_usecase.execute(email, "dummy_password", "User", "Auth System")
        
        return jsonify({
            'success': True,
            'totp_uri': uri,
            'message': 'TOTP configured successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@totp_bp.route('/qr', methods=['GET'])
def get_qr():
    """Obtener código QR para TOTP"""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email parameter is required'}), 400
        
        secret = user_repo.get_secret_by_email(email)
        if not secret:
            return jsonify({'error': 'User not found or TOTP not configured'}), 404
        
        img_bytes = generate_qr_usecase.execute(secret, email, 'Auth System')
        return Response(img_bytes, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@totp_bp.route('/verify', methods=['POST'])
def verify_totp():
    """Verificar código TOTP"""
    try:
        data = request.get_json()
        email = data.get('email')
        code = data.get('code')
        
        if not email or not code:
            return jsonify({'error': 'Email and code are required'}), 400
        
        if len(code) != 6:
            return jsonify({'error': 'Code must be 6 digits'}), 400
        
        secret = user_repo.get_secret_by_email(email)
        if not secret:
            return jsonify({'error': 'TOTP not configured for this user'}), 404
        
        validate_usecase = ValidateTOTPUseCase(secret)
        is_valid = validate_usecase.execute(code)
        
        if is_valid:
            return jsonify({
                'valid': True,
                'message': 'TOTP verified successfully'
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': 'Invalid TOTP code'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@totp_bp.route('/user-info', methods=['GET'])
def user_info():
    """Obtener información del usuario"""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email parameter is required'}), 400
        
        user = user_repo.find_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'email': user['email'],
            'first_name': user.get('first_name', ''),
            'auth_method': user.get('auth_method', 'totp')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500