from flask import Blueprint, request, jsonify, session
from ...application.email_otp_usecases import EmailOTPUseCases
from shared.models.user_model import UserRepository

# Crear blueprint
email_otp_blueprint = Blueprint('email_otp', __name__)
email_otp_usecases = EmailOTPUseCases()
user_repo = UserRepository()

@email_otp_blueprint.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Verificar que el usuario existe
        user = user_repo.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verificar que el usuario usa método email
        if user.get('auth_method') != 'email':
            return jsonify({'error': 'User is not registered with email method'}), 400
        
        result = email_otp_usecases.send_otp(email)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully',
                'email': email
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['message']
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_otp_blueprint.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        # Verificar que el usuario existe
        user = user_repo.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verificar que el usuario usa método email
        if user.get('auth_method') != 'email':
            return jsonify({'error': 'User is not registered with email method'}), 400
        
        result = email_otp_usecases.verify_otp(email, otp)
        
        if result['success']:
            # ✅ ESTABLECER LA SESIÓN SOLO DESPUÉS DE VERIFICAR OTP CORRECTAMENTE
            session['email'] = email
            print(f"✅ Sesión establecida para: {email} después de verificación OTP")
            
            # Marcar usuario como verificado
            user_repo.update_user(email, {'verified': True})
            
            return jsonify({
                'success': True,
                'message': 'OTP verified successfully',
                'email': email
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_otp_blueprint.route('/user-info', methods=['GET'])
def user_info():
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email parameter is required'}), 400
        
        user = user_repo.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verificar que sea usuario email
        if user.get('auth_method') != 'email':
            return jsonify({'error': 'User is not registered with email method'}), 400
        
        return jsonify({
            'email': user['email'],
            'first_name': user.get('first_name', ''),
            'auth_method': user.get('auth_method', 'email'),
            'verified': user.get('verified', False)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500