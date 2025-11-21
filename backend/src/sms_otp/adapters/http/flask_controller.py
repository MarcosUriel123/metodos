from flask import Blueprint, request, jsonify
from ...application.sms_otp_usecases import SendOTPUseCase, VerifyOTPUseCase
from ...infrastructure.twilio_sms_adapter import TwilioSMSAdapter

sms_bp = Blueprint('sms', __name__)

# Inicializar casos de uso
sms_service = TwilioSMSAdapter()
send_otp_uc = SendOTPUseCase(sms_service)
verify_otp_uc = VerifyOTPUseCase()

@sms_bp.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400
        
        success = send_otp_uc.execute(phone)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        phone = data.get('phone')
        code = data.get('code')
        
        if not phone or not code:
            return jsonify({'error': 'Phone and code are required'}), 400
        
        is_valid = verify_otp_uc.execute(phone, code)
        
        if is_valid:
            return jsonify({
                'valid': True,
                'message': 'OTP verified successfully'
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired OTP'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500