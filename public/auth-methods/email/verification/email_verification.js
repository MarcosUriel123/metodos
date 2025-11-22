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
    console.log('🔐 Email Verification page loaded');
    
    const verificationForm = document.getElementById('verificationForm');
    const verifyBtn = document.getElementById('verifyBtn');
    const resendBtn = document.getElementById('resendBtn');
    const verificationMessage = document.getElementById('verificationMessage');
    const userEmailElement = document.getElementById('userEmail');
    const timerElement = document.getElementById('timer');
    const resendTimerElement = document.getElementById('resendTimer');
    
    let timerInterval;
    let resendTimerInterval;
    let timeLeft = 120;
    let resendTimeLeft = 120;

    // Obtener email del localStorage
    const userEmail = localStorage.getItem('pending_verification_email') || localStorage.getItem('user_email');
    
    if (!userEmail) {
        showMessage('❌ No se encontró información de verificación. Por favor regresa al registro.', 'error');
        setTimeout(() => {
            window.location.href = '../../../access/sign_in/singin.html';
        }, 3000);
        return;
    }

    // Mostrar email del usuario
    if (userEmailElement) {
        userEmailElement.textContent = userEmail;
    }

    // Inicializar inputs OTP
    const otpDigits = [
        document.getElementById('digit1'),
        document.getElementById('digit2'),
        document.getElementById('digit3'),
        document.getElementById('digit4'),
        document.getElementById('digit5'),
        document.getElementById('digit6')
    ];

    // Manejar navegación entre inputs OTP
    otpDigits.forEach((digit, index) => {
        digit.addEventListener('input', (e) => {
            const value = e.target.value;
            
            if (value && !/^\d+$/.test(value)) {
                e.target.value = '';
                return;
            }
            
            if (value && index < otpDigits.length - 1) {
                otpDigits[index + 1].focus();
            }
            
            updateDigitStyles();
        });
        
        digit.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace') {
                if (!digit.value && index > 0) {
                    otpDigits[index - 1].focus();
                }
            }
        });
        
        digit.addEventListener('paste', (e) => {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text');
            if (/^\d{6}$/.test(pasteData)) {
                const digits = pasteData.split('');
                digits.forEach((digitValue, digitIndex) => {
                    if (otpDigits[digitIndex]) {
                        otpDigits[digitIndex].value = digitValue;
                    }
                });
                updateDigitStyles();
                otpDigits[5].focus();
            }
        });
    });

    function updateDigitStyles() {
        otpDigits.forEach(digit => {
            if (digit.value) {
                digit.classList.add('filled');
            } else {
                digit.classList.remove('filled');
            }
        });
    }

    function getOTPCode() {
        return otpDigits.map(digit => digit.value).join('');
    }

    function showMessage(message, type) {
        if (verificationMessage) {
            verificationMessage.textContent = message;
            verificationMessage.className = `verification-message message-${type}`;
            verificationMessage.style.display = 'block';
            
            verificationMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            if (type !== 'success') {
                setTimeout(() => {
                    if (verificationMessage.textContent === message) {
                        verificationMessage.style.display = 'none';
                    }
                }, 5000);
            }
        }
        console.log(`💬 [${type}] ${message}`);
    }

    function startTimer() {
        clearInterval(timerInterval);
        timeLeft = 120;
        
        timerInterval = setInterval(() => {
            timeLeft--;
            
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            if (timerElement) {
                timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                if (timeLeft <= 30) {
                    timerElement.classList.add('warning');
                }
            }
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                showMessage('⚠️ El código ha expirado. Por favor solicita uno nuevo.', 'error');
            }
        }, 1000);
    }

    function startResendTimer() {
        clearInterval(resendTimerInterval);
        resendTimeLeft = 120;
        resendBtn.disabled = true;
        
        resendTimerInterval = setInterval(() => {
            resendTimeLeft--;
            
            if (resendTimerElement) {
                resendTimerElement.textContent = `(${resendTimeLeft})`;
            }
            
            if (resendTimeLeft <= 0) {
                clearInterval(resendTimerInterval);
                resendBtn.disabled = false;
                resendTimerElement.textContent = '';
            }
        }, 1000);
    }

    // ✅ MANEJAR VERIFICACIÓN DEL CÓDIGO - CORREGIDO CON API_URL
    if (verificationForm) {
        verificationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const otpCode = getOTPCode();
            
            if (otpCode.length !== 6) {
                showMessage('❌ Por favor ingresa el código completo de 6 dígitos', 'error');
                return;
            }

            try {
                showMessage('⏳ Verificando código...', 'info');
                verifyBtn.classList.add('loading');
                verifyBtn.disabled = true;

                console.log('🔍 Verificando código OTP...');
                
                // ✅ CAMBIO AQUÍ: Usar API_URL en lugar de localhost fijo
                const response = await fetch(`${API_URL}/api/auth/email/verify-otp`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ 
                        email: userEmail, 
                        otp: otpCode 
                    })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                if (response.ok && data.success) {
                    showMessage('✅ Código verificado exitosamente. Redirigiendo...', 'success');
                    
                    // ✅ ESTABLECER ESTADO DE AUTENTICACIÓN DESPUÉS DE VERIFICAR OTP
                    localStorage.setItem('isAuthenticated', 'true');
                    localStorage.setItem('auth_method', 'email');
                    localStorage.setItem('user_email', userEmail);
                    
                    // Limpiar datos temporales
                    localStorage.removeItem('pending_verification_email');
                    
                    console.log('✅ Estado de autenticación establecido para Email OTP');
                    
                    // Redirigir al dashboard después de 2 segundos
                    setTimeout(() => {
                        window.location.href = '../../../index.html';
                    }, 2000);
                } else {
                    showMessage('❌ Error: ' + (data.error || 'Código inválido'), 'error');
                    verifyBtn.classList.remove('loading');
                    verifyBtn.disabled = false;
                    
                    // Limpiar inputs en caso de error
                    otpDigits.forEach(digit => {
                        digit.value = '';
                        digit.classList.remove('filled');
                    });
                    otpDigits[0].focus();
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage('❌ Error de conexión con el servidor', 'error');
                verifyBtn.classList.remove('loading');
                verifyBtn.disabled = false;
            }
        });
    }

    // ✅ MANEJAR REENVÍO DE CÓDIGO - CORREGIDO CON API_URL
    if (resendBtn) {
        resendBtn.addEventListener('click', async () => {
            try {
                showMessage('⏳ Reenviando código...', 'info');
                resendBtn.disabled = true;

                console.log('🔄 Reenviando código OTP...');
                
                // ✅ CAMBIO AQUÍ: Usar API_URL en lugar de localhost fijo
                const response = await fetch(`${API_URL}/api/auth/resend-otp`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ email: userEmail })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                if (response.ok) {
                    showMessage('✅ Código reenviado exitosamente', 'success');
                    startTimer();
                    startResendTimer();
                    
                    // Limpiar inputs
                    otpDigits.forEach(digit => {
                        digit.value = '';
                        digit.classList.remove('filled');
                    });
                    otpDigits[0].focus();
                } else {
                    showMessage('❌ Error: ' + (data.error || 'No se pudo reenviar el código'), 'error');
                    resendBtn.disabled = false;
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage('❌ Error de conexión con el servidor', 'error');
                resendBtn.disabled = false;
            }
        });
    }

    // Inicializar timers
    startTimer();
    startResendTimer();

    // Auto-focus en el primer input
    if (otpDigits[0]) {
        otpDigits[0].focus();
    }

    // Limpiar intervalos cuando se cierre la página
    window.addEventListener('beforeunload', () => {
        clearInterval(timerInterval);
        clearInterval(resendTimerInterval);
    });
});