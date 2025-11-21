// ✅ DETECCIÓN MEJORADA - FUNCIONA EN LOCAL Y PRODUCCIÓN
const API_URL = (() => {
    const hostname = window.location.hostname;
    console.log('🔍 Detección ambiente - hostname:', hostname, 'port:', window.location.port);
    
    // Desarrollo: localhost, 127.0.0.1, o cualquier URL con puerto
    if (hostname === 'localhost' || 
        hostname === '127.0.0.1' ||
        window.location.port !== '') {
        console.log('🎯 MODO DESARROLLO - Usando localhost:5000');
        return 'http://localhost:5000';
    } else {
        console.log('🚀 MODO PRODUCCIÓN - Usando Render.com');
        return 'https://metodos-scwr.onrender.com';
    }
})();

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Verification page loaded');
    
    const otpInput = document.getElementById('otp');
    const verifyButton = document.getElementById('verifyOTP');
    const resendButton = document.getElementById('resendOTP');
    const messageDiv = document.getElementById('message');

    // Auto-focus en el input
    if (otpInput) {
        otpInput.focus();
    }

    // ✅ FUNCIÓN MEJORADA: Obtener información del usuario
    async function getUserInfo(email) {
        try {
            console.log('📞 Buscando información del usuario:', email);
            
            // ✅ INTENTAR PRIMERO CON SMS, LUEGO CON EMAIL GENERAL - CORREGIDO CON API_URL
            let response = await fetch(`${API_URL}/api/auth/sms/user-info?email=${encodeURIComponent(email)}`, {
                method: 'GET',
                credentials: 'include'
            });
            
            if (!response.ok) {
                // Si falla SMS, intentar con el endpoint general
                console.log('⚠️ No se encontró en SMS, intentando con endpoint general...');
                response = await fetch(`${API_URL}/api/auth/user-info?email=${encodeURIComponent(email)}`, {
                    method: 'GET',
                    credentials: 'include'
                });
            }
            
            if (response.ok) {
                const userData = await response.json();
                console.log('📱 Información del usuario encontrada:', userData);
                return userData;
            } else {
                const errorData = await response.json();
                console.error('❌ Error obteniendo información del usuario:', errorData.error);
            }
        } catch (error) {
            console.error('❌ Error obteniendo información del usuario:', error);
        }
        return null;
    }

    // ✅ FUNCIÓN MEJORADA: Obtener email de múltiples fuentes
    function getVerificationEmail() {
        // Buscar en múltiples fuentes posibles
        const email = localStorage.getItem('pending_verification_email') || 
                     localStorage.getItem('user_email') ||
                     sessionStorage.getItem('verification_email');
        
        console.log('🔍 Buscando email para verificación:', {
            pending_verification: localStorage.getItem('pending_verification_email'),
            user_email: localStorage.getItem('user_email'),
            session_storage: sessionStorage.getItem('verification_email')
        });
        
        return email;
    }

    // Verificar OTP
    if (verifyButton) {
        verifyButton.addEventListener('click', async () => {
            console.log('🔍 Verify button clicked');
            
            const otp = otpInput.value.trim();
            const email = getVerificationEmail();
            
            if (!otp || otp.length !== 6) {
                showMessage('Por favor ingresa un código válido de 6 dígitos', 'error');
                return;
            }

            if (!email) {
                showMessage('❌ No se encontró información de verificación. Regresa al login.', 'error');
                
                // Redirigir al login después de 3 segundos
                setTimeout(() => {
                    window.location.href = "../log_in/login.html";
                }, 3000);
                return;
            }

            verifyButton.disabled = true;
            verifyButton.textContent = 'Verificando...';

            try {
                console.log('📤 Sending verification request...');
                
                // ✅ OBTENER INFORMACIÓN COMPLETA DEL USUARIO
                const userInfo = await getUserInfo(email);
                
                if (!userInfo || !userInfo.phone_number) {
                    showMessage('❌ No se encontró información del usuario. Regresa al login.', 'error');
                    verifyButton.disabled = false;
                    verifyButton.textContent = 'Verificar';
                    
                    setTimeout(() => {
                        window.location.href = "../log_in/login.html";
                    }, 3000);
                    return;
                }

                console.log('📱 Verificando OTP para teléfono:', userInfo.phone_number);
                
                // ✅ ENVIAR PARÁMETROS CORRECTOS - CORREGIDO CON API_URL
                const response = await fetch(`${API_URL}/api/auth/sms/verify-otp`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ 
                        phone: userInfo.phone_number,
                        code: otp
                    })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                if (response.ok && data.valid) {
                    showMessage('✅ Verificación exitosa. Redirigiendo...', 'success');
                    
                    // ✅ GUARDAR SESIÓN ANTES DE LIMPIAR
                    localStorage.setItem('auth_method', 'sms');
                    localStorage.setItem('isAuthenticated', 'true');
                    localStorage.setItem('user_email', email);
                    
                    if (userInfo.first_name) {
                        localStorage.setItem('user_first_name', userInfo.first_name);
                    }
                    
                    // ✅ LIMPIAR SOLO EL EMAIL TEMPORAL, MANTENER user_email
                    localStorage.removeItem('pending_verification_email');
                    sessionStorage.removeItem('verification_email');
                    
                    // ✅ REDIRECCIÓN
                    setTimeout(() => {
                        window.location.href = "../../../index/index.html";
                    }, 1500);
                } else {
                    showMessage(data.error || '❌ Código inválido', 'error');
                    otpInput.value = '';
                    otpInput.focus();
                    
                    verifyButton.disabled = false;
                    verifyButton.textContent = 'Verificar';
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage('❌ Error de conexión', 'error');
                
                verifyButton.disabled = false;
                verifyButton.textContent = 'Verificar';
            }
        });
    }

    if (resendButton) {
        resendButton.addEventListener('click', async () => {
            console.log('🔄 Resend button clicked');
            
            resendButton.disabled = true;
            resendButton.textContent = 'Enviando...';

            try {
                // ✅ USAR LA FUNCIÓN MEJORADA PARA OBTENER EMAIL
                const email = getVerificationEmail();
                console.log('📧 Email para reenvío:', email);
                
                if (!email) {
                    showMessage('❌ No se encontró información de verificación. Regresa al login.', 'error');
                    resendButton.disabled = false;
                    resendButton.textContent = 'Reenviar código';
                    
                    setTimeout(() => {
                        window.location.href = "../log_in/login.html";
                    }, 3000);
                    return;
                }

                // ✅ OBTENER EL NÚMERO DE TELÉFONO DEL USUARIO
                const userInfo = await getUserInfo(email);
                
                if (!userInfo || !userInfo.phone_number) {
                    showMessage('❌ No se encontró número de teléfono para este usuario', 'error');
                    resendButton.disabled = false;
                    resendButton.textContent = 'Reenviar código';
                    return;
                }

                console.log('📱 Reenviando OTP a teléfono:', userInfo.phone_number);

                // ✅ USAR ENDPOINT CORRECTO CON PHONE NUMBER - CORREGIDO CON API_URL
                const response = await fetch(`${API_URL}/api/auth/sms/send-otp`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ 
                        phone: userInfo.phone_number  // ✅ CORREGIDO: Enviar phone number, no email
                    })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response:', data);

                if (response.ok) {
                    showMessage('✅ Nuevo código enviado por SMS', 'success');
                    otpInput.value = '';
                    otpInput.focus();
                    
                    // ✅ INICIAR TIMER DE REENVÍO
                    startResendTimer();
                } else {
                    showMessage(data.error || '❌ Error al reenviar el código', 'error');
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage('❌ Error de conexión', 'error');
            } finally {
                resendButton.disabled = false;
                resendButton.textContent = 'Reenviar código';
            }
        });
    }

    // ✅ TIMER PARA REENVÍO
    function startResendTimer() {
        let timeLeft = 60;
        resendButton.disabled = true;
        
        const timerInterval = setInterval(() => {
            resendButton.textContent = `Reenviar (${timeLeft}s)`;
            timeLeft--;
            
            if (timeLeft < 0) {
                clearInterval(timerInterval);
                resendButton.disabled = false;
                resendButton.textContent = 'Reenviar código';
            }
        }, 1000);
    }

    // Permitir Enter para verificar
    if (otpInput) {
        otpInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && verifyButton && !verifyButton.disabled) {
                verifyButton.click();
            }
        });
    }

    function showMessage(text, type) {
        if (messageDiv) {
            messageDiv.textContent = text;
            messageDiv.className = type;
            messageDiv.style.display = 'block';
            
            // Auto-ocultar mensajes de error después de 5 segundos
            if (type === 'error') {
                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
            }
        }
        console.log(`💬 [${type}] ${text}`);
    }

    // ✅ VERIFICACIÓN MEJORADA AL CARGAR LA PÁGINA
    const verificationEmail = getVerificationEmail();
    if (verificationEmail) {
        console.log('✅ Email encontrado para verificación:', verificationEmail);
        showMessage(`📱 Ingresa el código enviado por SMS para ${verificationEmail}`, 'info');
        
        // ✅ GUARDAR EN SESSIONSTORAGE COMO RESPALDO
        sessionStorage.setItem('verification_email', verificationEmail);
    } else {
        console.log('⚠️ No se encontró email para verificación');
        showMessage('⚠️ Sesión no encontrada. Serás redirigido al login.', 'error');
        
        // Redirigir automáticamente después de 3 segundos
        setTimeout(() => {
            window.location.href = "../log_in/login.html";
        }, 3000);
    }

    // ✅ LIMPIAR SESSIONSTORAGE AL CERRAR LA PESTAÑA
    window.addEventListener('beforeunload', () => {
        sessionStorage.removeItem('verification_email');
    });
});