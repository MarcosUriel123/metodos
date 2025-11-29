from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from flask_cors import CORS
from datetime import datetime

# 🔧 SOLUCIÓN DE IMPORTACIONES
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Cargar variables de entorno
load_dotenv()

# Importar blueprints existentes
from sms_otp.adapters.http.flask_controller import sms_bp
from totp.adapters.http.flask_controller import totp_bp

# ✅ NUEVO: Importar blueprint de Email OTP - CORREGIDO para email_otp
try:
    from email_otp.adapters.http.flask_controller import email_otp_blueprint
    EMAIL_OTP_AVAILABLE = True
    print("✅ Módulo Email OTP cargado correctamente")
except ImportError as e:
    EMAIL_OTP_AVAILABLE = False
    print(f"⚠️ Módulo Email OTP no disponible: {e}")

# ✅ NUEVO: Importar blueprint de Password Recovery
try:
    from password_recovery.adapters.http.flask_controller import password_recovery_bp
    PASSWORD_RECOVERY_AVAILABLE = True
    print("✅ Módulo Password Recovery cargado correctamente")
except ImportError as e:
    PASSWORD_RECOVERY_AVAILABLE = False
    print(f"⚠️ Módulo Password Recovery no disponible: {e}")
    
# Importar casos de uso existentes
from sms_otp.application.sms_otp_usecases import SendOTPUseCase, VerifyOTPUseCase
from sms_otp.infrastructure.twilio_sms_adapter import TwilioSMSAdapter
from shared.models.user_model import UserRepository
from totp.application.register_user_usecase import RegisterUserUseCase
from totp.infrastructure.totp_repository import TOTPRepository

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# Registrar servicios existentes
app.register_blueprint(sms_bp, url_prefix='/api/auth/sms')
app.register_blueprint(totp_bp, url_prefix='/api/auth/totp')

# ✅ NUEVO: Registrar blueprint de Email OTP si está disponible
if EMAIL_OTP_AVAILABLE:
    app.register_blueprint(email_otp_blueprint, url_prefix='/api/auth/email')

# ✅ NUEVO: Registrar blueprint de Password Recovery si está disponible
if PASSWORD_RECOVERY_AVAILABLE:
    app.register_blueprint(password_recovery_bp, url_prefix='/api/auth/password-recovery')
    print("✅ Blueprint de Password Recovery registrado")

# Inicializar servicios existentes
user_repo = UserRepository()
sms_service = TwilioSMSAdapter()
send_otp_use_case = SendOTPUseCase(sms_service)
verify_otp_use_case = VerifyOTPUseCase()
totp_register_usecase = RegisterUserUseCase(TOTPRepository())

# Solo pending_verifications en memoria (sesiones activas)
pending_verifications = {}

# ✅ REGISTRO UNIFICADO - CORREGIDO PARA EMAIL OTP
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
        
        # ✅ NUEVO: Validación para Email OTP (no requiere phone_number)
        if auth_method == 'sms' and not phone_number:
            return jsonify({'error': 'Phone number is required for SMS authentication'}), 400
        
        # ✅ NUEVO: Manejar registro para Email OTP - CORREGIDO
        if auth_method == 'email':
            if not EMAIL_OTP_AVAILABLE:
                return jsonify({'error': 'Email OTP service is not available'}), 500
                
            # Guardar usuario para Email OTP (sin phone_number)
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
            
            # Enviar OTP por email inmediatamente después del registro
            from email_otp.application.email_otp_usecases import EmailOTPUseCases
            email_otp_usecases = EmailOTPUseCases()
            email_result = email_otp_usecases.send_otp(email)
            
            if email_result['success']:
                pending_verifications[email] = email  # Para tracking
                # ✅ NO establecer session['email'] aquí - el usuario debe verificar OTP primero
                
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
                # El usuario se registró pero falló el envío del email
                return jsonify({
                    'success': True,
                    'message': 'User registered but failed to send OTP email',
                    'requires_otp': True,
                    'auth_method': 'email',
                    'email': email
                }), 200
        
        # Manejar SMS (existente - SIN CAMBIOS)
        elif auth_method == 'sms':
            # Guardar usuario para SMS
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
            
            # Enviar OTP INMEDIATAMENTE
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
        
        else:  # TOTP (existente - SIN CAMBIOS)
            # Registrar usuario con TOTP
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

# ✅ LOGIN UNIFICADO - CORREGIDO DEFINITIVAMENTE PARA EMAIL OTP
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
        
        # BUSCAR EN MONGODB
        user = user_repo.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user['password'] != password:
            return jsonify({'error': 'Invalid password'}), 401
        
        auth_method = user.get('auth_method', 'sms')
        
        print(f"✅ Credenciales válidas para: {email}, método: {auth_method}")
        
        # ✅ NUEVO: Manejar login para Email OTP - SIN SESIÓN INMEDIATA
        if auth_method == 'email':
            if not EMAIL_OTP_AVAILABLE:
                return jsonify({'error': 'Email OTP service is not available'}), 500
                
            print(f"📤 ENVIANDO OTP por email a: {email}")
            
            # CORREGIDO: Importación desde carpeta "email_otp"
            from email_otp.application.email_otp_usecases import EmailOTPUseCases
            email_otp_usecases = EmailOTPUseCases()
            email_result = email_otp_usecases.send_otp(email)
            
            if email_result['success']:
                pending_verifications[email] = email
                print(f"✅ OTP enviado exitosamente por email")
                
                # ✅ NO establecer session['email'] aquí - solo después de verificar OTP
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
        
        # Manejar SMS (existente - SIN CAMBIOS)
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
        
        else:  # TOTP (existente - SIN CAMBIOS)
            requires_otp = bool(user.get('secret'))
            
            # ✅ SOLO PARA TOTP: Establecer sesión si no requiere OTP inmediato
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

# ✅ RESEND OTP - ACTUALIZADO CON EMAIL OTP
@app.route('/api/auth/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json()
        email = data.get('email') or session.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Buscar usuario para determinar el método de autenticación
        user = user_repo.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        auth_method = user.get('auth_method', 'sms')
        
        # ✅ NUEVO: Manejar reenvío para Email OTP
        if auth_method == 'email':
            if not EMAIL_OTP_AVAILABLE:
                return jsonify({'error': 'Email OTP service is not available'}), 500
                
            # CORREGIDO: Importación desde carpeta "email_otp"
            from email_otp.application.email_otp_usecases import EmailOTPUseCases
            email_otp_usecases = EmailOTPUseCases()
            email_result = email_otp_usecases.send_otp(email)
            
            if email_result['success']:
                return jsonify({'message': 'OTP resent successfully to email'}), 200
            else:
                return jsonify({'error': 'Failed to resend OTP email'}), 500
        
        # Manejar SMS (existente - SIN CAMBIOS)
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
        
        # BUSCAR USUARIO POR TELÉFONO
        user = user_repo.find_by_phone(phone_number)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'No user found with this phone number'
            }), 404
        
        email = user['email']
        
        # CONFIGURAR SESIÓN
        session.clear()
        session['email'] = email
        session['phone_number'] = phone_number
        pending_verifications[email] = phone_number
        
        # ENVIAR OTP
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

# ✅ ENDPOINT PARA OBTENER USUARIO SMS (existente - SIN CAMBIOS)
@app.route('/api/auth/sms/user-info', methods=['GET'])
def sms_user_info():
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email parameter is required'}), 400
        
        user = user_repo.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verificar que sea usuario SMS
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

# ✅ LOGOUT ENDPOINT (existente - SIN CAMBIOS)
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        print("✅ Sesión cerrada correctamente")
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        print(f"❌ Error en logout: {e}")
        return jsonify({'error': str(e)}), 500

# ✅ RUTAS PRINCIPALES - ACTUALIZADO CON EMAIL OTP
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
    
    # ✅ NUEVO: Agregar endpoints de Email OTP si está disponible
    if EMAIL_OTP_AVAILABLE:
        endpoints["email"] = {
            "send_otp": "POST /api/auth/email/send-otp",
            "verify_otp": "POST /api/auth/email/verify-otp", 
            "user_info": "GET /api/auth/email/user-info?email=user@example.com"
        }
    
    # ✅ NUEVO: Agregar endpoints de Password Recovery si está disponible
    if PASSWORD_RECOVERY_AVAILABLE:
        endpoints["password_recovery"] = {
            "request": "POST /api/auth/password-recovery/request",
            "verify_otp": "POST /api/auth/password-recovery/verify-otp",
            "reset": "POST /api/auth/password-recovery/reset"
        }
    
    return jsonify({
        "message": "Sistema de Autenticación Unificado",
        "available_services": ["sms", "totp", "email", "password_recovery"] if EMAIL_OTP_AVAILABLE and PASSWORD_RECOVERY_AVAILABLE else ["sms", "totp", "password_recovery"] if PASSWORD_RECOVERY_AVAILABLE else ["sms", "totp"],
        "endpoints": endpoints
    })

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
        "port": 5000
    })

# ✅ ENDPOINT GENERAL PARA OBTENER INFORMACIÓN DEL USUARIO (existente - SIN CAMBIOS)
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
    print("🚀 Servidor de Autenticación Unificado iniciado")
    print("📡 http://localhost:5000")
    print("🔐 Servicios disponibles:")
    print("   - SMS OTP: /api/auth/sms/*")
    print("   - TOTP: /api/auth/totp/*") 
    if EMAIL_OTP_AVAILABLE:
        print("   - Email OTP: /api/auth/email/*")
    if PASSWORD_RECOVERY_AVAILABLE:
        print("   - Password Recovery: /api/auth/password-recovery/*")
    print("   - Auth: /api/auth/register, /api/auth/login, /api/auth/logout, etc.")
    print("=" * 50)
    app.run(debug=True, port=5000)

    CORS(app, 
        supports_credentials=True,
        origins=[
            "http://localhost:*",
            "http://127.0.0.1:*", 
            "https://*.vercel.app",
            "https://metodos-two.vercel.app"
        ]
)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)