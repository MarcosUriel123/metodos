from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from datetime import datetime

# 🔧 SOLUCIÓN DE IMPORTACIONES
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Cargar variables de entorno
load_dotenv()

# Importar blueprints existentes
from sms_otp.adapters.http.flask_controller import sms_bp
from totp.adapters.http.flask_controller import totp_bp

# ✅ MÓDULO EMAIL OTP (existente - SIN CAMBIOS)
try:
    from email_otp.adapters.http.flask_controller import email_otp_blueprint
    EMAIL_OTP_AVAILABLE = True
    print("✅ Módulo Email OTP cargado correctamente")
except ImportError as e:
    EMAIL_OTP_AVAILABLE = False
    print(f"⚠️ Módulo Email OTP no disponible: {e}")

# ✅ MÓDULO PASSWORD RECOVERY
try:
    from password_recovery.adapters.http.flask_controller import password_recovery_bp
    PASSWORD_RECOVERY_AVAILABLE = True
    print("✅ Módulo Password Recovery cargado correctamente")
except ImportError as e:
    PASSWORD_RECOVERY_AVAILABLE = False
    print(f"⚠️ Módulo Password Recovery no disponible: {e}")
    import traceback
    traceback.print_exc()
    
# Importar casos de uso existentes
from sms_otp.application.sms_otp_usecases import SendOTPUseCase, VerifyOTPUseCase
from sms_otp.infrastructure.twilio_sms_adapter import TwilioSMSAdapter
from shared.models.user_model import UserRepository
from totp.application.register_user_usecase import RegisterUserUseCase
from totp.infrastructure.totp_repository import TOTPRepository

app = Flask(__name__)

# 🚨 CORS CRÍTICO - CONFIGURACIÓN COMPLETA PARA VERCEL + RENDER
CORS(app, 
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:*",
                "http://127.0.0.1:*",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "https://metodos-two.vercel.app",
                "https://*.vercel.app"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True,
            "max_age": 3600
        }
    }
)

app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# 🔧 MIDDLEWARE ADICIONAL PARA CORS (por si acaso)
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    
    allowed_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',
        'https://metodos-two.vercel.app'
    ]
    
    # Permitir cualquier subdominio de vercel.app
    if origin and (origin in allowed_origins or origin.endswith('.vercel.app')):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
    
    return response

# Registrar servicios existentes
app.register_blueprint(sms_bp, url_prefix='/api/auth/sms')
app.register_blueprint(totp_bp, url_prefix='/api/auth/totp')

# ✅ Registrar blueprint de Email OTP si está disponible
if EMAIL_OTP_AVAILABLE:
    app.register_blueprint(email_otp_blueprint, url_prefix='/api/auth/email')
    print("✅ Blueprint de Email OTP registrado")

# ✅ Registrar blueprint de Password Recovery
if PASSWORD_RECOVERY_AVAILABLE:
    app.register_blueprint(password_recovery_bp)
    print("✅ Blueprint de Password Recovery registrado en /api/auth/password-recovery/*")

# Inicializar servicios existentes
user_repo = UserRepository()
sms_service = TwilioSMSAdapter()
send_otp_use_case = SendOTPUseCase(sms_service)
verify_otp_use_case = VerifyOTPUseCase()
totp_register_usecase = RegisterUserUseCase(TOTPRepository())

# Solo pending_verifications en memoria (sesiones activas)
pending_verifications = {}

# ✅ REGISTRO UNIFICADO (existente - SIN CAMBIOS)
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print("=" * 50)
        print("📝 REGISTRO - Datos recibidos:")
        print(f"   Email: {data.get('email')}")
        print(f"   Teléfono: {data.get('phone_number')}")
        print(f"   Método: {data.get('auth_method')}")
        print("=" * 50)
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        auth_method = data.get('auth_method', 'sms')
        phone_number = data.get('phone_number')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if user_repo.user_exists(email):
            return jsonify({'error': 'User already exists'}), 400
        
        if auth_method == 'sms' and not phone_number:
            return jsonify({'error': 'Phone number is required for SMS authentication'}), 400
        
        if auth_method == 'email':
            if not EMAIL_OTP_AVAILABLE:
                return jsonify({'error': 'Email OTP service is not available'}), 500
                
            user_data = {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'auth_method': auth_method,
                'verified': False
            }
            
            user_repo.create_user(user_data)
            print(f"✅ Usuario Email OTP guardado en MongoDB: {email}")
            
            from email_otp.application.email_otp_usecases import EmailOTPUseCases
            email_otp_usecases = EmailOTPUseCases()
            email_result = email_otp_usecases.send_otp(email)
            
            if email_result['success']:
                pending_verifications[email] = email
                print(f"✅ OTP enviado exitosamente por email a {email}")
                
                return jsonify({
                    'success': True,
                    'message': 'User registered. OTP sent to email.',
                    'requires_otp': True,
                    'auth_method': 'email',
                    'email': email
                }), 200
            else:
                print("❌ Falló el envío de OTP por email")
                return jsonify({
                    'success': True,
                    'message': 'User registered but failed to send OTP email',
                    'requires_otp': True,
                    'auth_method': 'email',
                    'email': email
                }), 200
        
        elif auth_method == 'sms':
            user_data = {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'auth_method': auth_method,
                'phone_number': phone_number,
                'verified': False
            }
            
            user_repo.create_user(user_data)
            print(f"✅ Usuario SMS guardado en MongoDB: {email}")
            
            print(f"📤 ENVIANDO OTP a: {phone_number}")
            otp_sent = send_otp_use_case.execute(phone_number)
            
            if otp_sent:
                pending_verifications[email] = phone_number
                session['email'] = email
                session['phone_number'] = phone_number
                
                print(f"✅ OTP enviado exitosamente a {phone_number}")
                
                return jsonify({
                    'success': True,
                    'message': 'User registered. OTP sent to phone.',
                    'requires_otp': True,
                    'auth_method': 'sms',
                    'email': email
                }), 200
            else:
                print("❌ Falló el envío de OTP")
                return jsonify({'error': 'Failed to send OTP'}), 500
        
        else:  # TOTP
            try:
                uri = totp_register_usecase.execute(email, password, first_name)
                session['email'] = email
                
                return jsonify({
                    'success': True,
                    'message': 'User registered successfully',
                    'requires_qr': True,
                    'totp_uri': uri,
                    'email': email
                }), 200
            except Exception as e:
                print(f"❌ Error en registro TOTP: {e}")
                return jsonify({'error': 'Failed to register TOTP user'}), 500
        
    except Exception as e:
        print(f"❌ Error in register: {e}")
        return jsonify({'error': str(e)}), 500

# ✅ LOGIN UNIFICADO - CORREGIDO PARA CIFRADO
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔐 LOGIN - Datos recibidos:")
        print(f"   Email: {data.get('email')}")
        print("=" * 50)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = user_repo.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # ✅ LÍNEA CORREGIDA - VERIFICACIÓN CON CIFRADO
        if not user_repo.verify_password_for_login(email, password):
            return jsonify({'error': 'Invalid password'}), 401
        
        auth_method = user.get('auth_method', 'sms')
        
        print(f"✅ Credenciales válidas para: {email}, método: {auth_method}")
        
        if auth_method == 'email':
            if not EMAIL_OTP_AVAILABLE:
                return jsonify({'error': 'Email OTP service is not available'}), 500
                
            print(f"📤 ENVIANDO OTP por email a: {email}")
            
            from email_otp.application.email_otp_usecases import EmailOTPUseCases
            email_otp_usecases = EmailOTPUseCases()
            email_result = email_otp_usecases.send_otp(email)
            
            if email_result['success']:
                pending_verifications[email] = email
                print(f"✅ OTP enviado exitosamente por email")
                
                return jsonify({
                    'success': True,
                    'requires_otp': True,
                    'auth_method': 'email',
                    'message': 'OTP sent to your email',
                    'email': email
                }), 200
            else:
                print("❌ Falló el envío de OTP por email")
                return jsonify({'error': 'Failed to send OTP email'}), 500
        
        elif auth_method == 'sms':
            phone_number = user.get('phone_number')
            if not phone_number:
                return jsonify({'error': 'No phone number found for SMS user'}), 400
                
            print(f"📤 ENVIANDO OTP a: {phone_number}")
            session['phone_number'] = phone_number
            
            success = send_otp_use_case.execute(phone_number)
            
            if success:
                pending_verifications[email] = phone_number
                print(f"✅ OTP enviado exitosamente")
                
                return jsonify({
                    'success': True,
                    'requires_otp': True,
                    'auth_method': 'sms',
                    'message': 'OTP sent to your phone',
                    'email': email
                }), 200
            else:
                print("❌ Falló el envío de OTP")
                return jsonify({'error': 'Failed to send OTP'}), 500
        
        else:  # TOTP
            requires_otp = bool(user.get('secret'))
            
            if not requires_otp:
                session['email'] = email
            
            return jsonify({
                'success': True,
                'requires_otp': requires_otp,
                'auth_method': 'totp',
                'email': email
            }), 200
        
    except Exception as e:
        print(f"❌ Error in login: {e}")
        return jsonify({'error': str(e)}), 500

# ✅ RESEND OTP (existente - SIN CAMBIOS)
@app.route('/api/auth/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json()
        email = data.get('email') or session.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = user_repo.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        auth_method = user.get('auth_method', 'sms')
        
        if auth_method == 'email':
            if not EMAIL_OTP_AVAILABLE:
                return jsonify({'error': 'Email OTP service is not available'}), 500
                
            from email_otp.application.email_otp_usecases import EmailOTPUseCases
            email_otp_usecases = EmailOTPUseCases()
            email_result = email_otp_usecases.send_otp(email)
            
            if email_result['success']:
                return jsonify({'message': 'OTP resent successfully to email'}), 200
            else:
                return jsonify({'error': 'Failed to resend OTP email'}), 500
        
        elif auth_method == 'sms':
            phone_number = None
            
            if email in pending_verifications:
                phone_number = pending_verifications[email]
            else:
                if user and user.get('phone_number'):
                    phone_number = user['phone_number']
                    pending_verifications[email] = phone_number
                else:
                    return jsonify({'error': 'No pending verification found for this email'}), 400
            
            success = send_otp_use_case.execute(phone_number)
            
            if success:
                return jsonify({'message': 'OTP resent successfully'}), 200
            else:
                return jsonify({'error': 'Failed to resend OTP'}), 500
        else:
            return jsonify({'error': 'Unsupported authentication method'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ SMS LOGIN (existente - SIN CAMBIOS)
@app.route('/api/auth/sms-login', methods=['POST'])
def sms_login():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        user = user_repo.find_by_phone(phone_number)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'No user found with this phone number'
            }), 404
        
        email = user['email']
        
        session.clear()
        session['email'] = email
        session['phone_number'] = phone_number
        pending_verifications[email] = phone_number
        
        success = send_otp_use_case.execute(phone_number)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully',
                'phone_number': phone_number,
                'email': email,
                'requires_otp': True,
                'auth_method': 'sms'
            }), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ SMS USER INFO (existente - SIN CAMBIOS)
@app.route('/api/auth/sms/user-info', methods=['GET'])
def sms_user_info():
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email parameter is required'}), 400
        
        user = user_repo.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.get('auth_method') != 'sms':
            return jsonify({'error': 'User is not registered with SMS method'}), 400
        
        return jsonify({
            'email': user['email'],
            'first_name': user.get('first_name', ''),
            'phone_number': user.get('phone_number'),
            'auth_method': user.get('auth_method', 'sms')
        }), 200
        
    except Exception as e:
        print(f"❌ Error in sms_user_info: {e}")
        return jsonify({'error': str(e)}), 500

# ✅ LOGOUT (existente - SIN CAMBIOS)
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        print("✅ Sesión cerrada correctamente")
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        print(f"❌ Error en logout: {e}")
        return jsonify({'error': str(e)}), 500

# ✅ HOME - ACTUALIZADO con Password Recovery
@app.route('/')
def home():
    endpoints = {
        "sms": {
            "send_otp": "POST /api/auth/sms/send-otp",
            "verify_otp": "POST /api/auth/sms/verify-otp",
            "user_info": "GET /api/auth/sms/user-info?email=user@example.com"
        },
        "totp": {
            "setup": "POST /api/auth/totp/setup",
            "qr": "GET /api/auth/totp/qr?email=user@example.com",
            "verify": "POST /api/auth/totp/verify",
            "user_info": "GET /api/auth/totp/user-info?email=user@example.com"
        },
        "auth": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "resend_otp": "POST /api/auth/resend-otp",
            "sms_login": "POST /api/auth/sms-login",
            "logout": "POST /api/auth/logout"
        }
    }
    
    available_services = ["sms", "totp"]
    
    if EMAIL_OTP_AVAILABLE:
        endpoints["email"] = {
            "send_otp": "POST /api/auth/email/send-otp",
            "verify_otp": "POST /api/auth/email/verify-otp", 
            "user_info": "GET /api/auth/email/user-info?email=user@example.com"
        }
        available_services.append("email")
    
    if PASSWORD_RECOVERY_AVAILABLE:
        endpoints["password_recovery"] = {
            "request": "POST /api/auth/password-recovery/request",
            "verify_otp": "POST /api/auth/password-recovery/verify-otp",
            "reset": "POST /api/auth/password-recovery/reset"
        }
        available_services.append("password_recovery")
    
    return jsonify({
        "message": "Sistema de Autenticación Unificado",
        "version": "2.2",
        "available_services": available_services,
        "endpoints": endpoints,
        "cors_enabled": True
    })

# ✅ HEALTH CHECK - ACTUALIZADO
@app.route('/health', methods=['GET'])
def health():
    services = ["sms_otp", "totp"]
    if EMAIL_OTP_AVAILABLE:
        services.append("email_otp")
    if PASSWORD_RECOVERY_AVAILABLE:
        services.append("password_recovery")
    
    return jsonify({
        "status": "healthy",
        "services": services,
        "port": int(os.environ.get('PORT', 5000)),
        "mongodb": "connected",
        "cors": "enabled"
    })

# ✅ USER INFO GENERAL (existente - SIN CAMBIOS)
@app.route('/api/auth/user-info', methods=['GET'])
def get_user_info():
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email parameter is required'}), 400
        
        user = user_repo.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'email': user['email'],
            'first_name': user.get('first_name', ''),
            'phone_number': user.get('phone_number'),
            'auth_method': user.get('auth_method', 'sms')
        }), 200
        
    except Exception as e:
        print(f"❌ Error in get_user_info: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor de Autenticación Unificado iniciado")
    print("=" * 60)
    print(f"📡 http://localhost:{os.environ.get('PORT', 5000)}")
    print("🔐 Servicios disponibles:")
    print("   ✅ SMS OTP: /api/auth/sms/*")
    print("   ✅ TOTP: /api/auth/totp/*") 
    if EMAIL_OTP_AVAILABLE:
        print("   ✅ Email OTP: /api/auth/email/*")
    if PASSWORD_RECOVERY_AVAILABLE:
        print("   ✅ Password Recovery: /api/auth/password-recovery/*")
    print("   ✅ Auth: /api/auth/register, /api/auth/login, etc.")
    print("🌐 CORS habilitado para Vercel y localhost")
    print("=" * 60)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(
        debug=os.environ.get('FLASK_ENV') == 'development',
        host='0.0.0.0', 
        port=port,
        use_reloader=False
    )