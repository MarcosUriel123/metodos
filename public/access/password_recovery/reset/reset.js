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
    console.log('🔐 Password Reset page loaded');
    
    // Elementos del DOM
    const resetForm = document.getElementById('resetForm');
    const resetBtn = document.getElementById('resetBtn');
    const otpInput = document.getElementById('otp');
    const newPasswordInput = document.getElementById('newPassword');
    const confirmNewPasswordInput = document.getElementById('confirmNewPassword');
    const toggleNewPassword = document.getElementById('toggleNewPassword');
    const toggleConfirmNewPassword = document.getElementById('toggleConfirmNewPassword');
    const resetMessage = document.getElementById('resetMessage');
    const userEmailElement = document.getElementById('userEmail');
    const passwordHint = document.querySelector('.password-hint');

    // ✅ CARGAR EMAIL DESDE LOCALSTORAGE
    const recoveryEmail = localStorage.getItem('recovery_email');
    if (recoveryEmail && userEmailElement) {
        userEmailElement.textContent = `Para: ${recoveryEmail}`;
        console.log('✅ Email cargado para recuperación:', recoveryEmail);
    } else {
        console.log('⚠️ No se encontró email de recuperación, redirigiendo...');
        showMessage('❌ No se encontró información de recuperación. Serás redirigido.', 'error');
        setTimeout(() => {
            window.location.href = '../request/request.html';
        }, 3000);
        return;
    }

    // ✅ VALIDACIÓN: Solo números en OTP
    if (otpInput) {
        otpInput.addEventListener('input', (e) => {
            // Permitir solo números
            let value = e.target.value;
            value = value.replace(/\D/g, '');
            
            // Limitar a 6 caracteres
            if (value.length > 6) {
                value = value.substring(0, 6);
            }
            
            e.target.value = value;
        });
    }

    // ✅ VALIDACIÓN: Contraseña en tiempo real - CORREGIDO
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', (e) => {
            const value = e.target.value;
            
            // Validar requisitos COMPLETOS
            const hasUpperCase = /[A-Z]/.test(value);
            const hasLowerCase = /[a-z]/.test(value);
            const hasNumber = /\d/.test(value);
            const hasNoSymbols = /^[a-zA-Z\d]*$/.test(value); // ✅ SOLO letras y números
            const isValidLength = value.length === 10;
            
            // Verificar si es válida COMPLETAMENTE
            const isValid = hasUpperCase && hasLowerCase && hasNumber && hasNoSymbols && isValidLength;
            
            // Actualizar hint con colores
            if (passwordHint) {
                let hintText = '';
                
                if (!isValidLength) {
                    hintText = `${value.length}/10 caracteres`;
                } else if (!hasNoSymbols) {
                    hintText = '❌ Símbolos no permitidos';  // ✅ PRIORIDAD para símbolos
                } else if (!hasUpperCase || !hasLowerCase || !hasNumber) {
                    hintText = 'Falta: ';
                    if (!hasUpperCase) hintText += 'mayúscula ';
                    if (!hasLowerCase) hintText += 'minúscula ';
                    if (!hasNumber) hintText += 'número';
                } else {
                    hintText = '✅ Contraseña válida';
                    passwordHint.style.color = '#10b981';
                }
                
                if (!isValid) {
                    passwordHint.style.color = '#ef4444';
                }
                
                passwordHint.textContent = hintText;
            }
        });
    }

    // Toggle password visibility
    if (toggleNewPassword) {
        toggleNewPassword.addEventListener('click', () => {
            const type = newPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            newPasswordInput.setAttribute('type', type);
            const icon = toggleNewPassword.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }

    if (toggleConfirmNewPassword) {
        toggleConfirmNewPassword.addEventListener('click', () => {
            const type = confirmNewPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmNewPasswordInput.setAttribute('type', type);
            const icon = toggleConfirmNewPassword.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }

    // Función para mostrar mensajes
    function showMessage(message, type) {
        if (resetMessage) {
            resetMessage.textContent = message;
            resetMessage.className = `reset-message message-${type}`;
            resetMessage.style.display = 'block';
            
            resetMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            if (type !== 'success') {
                setTimeout(() => {
                    if (resetMessage.textContent === message) {
                        resetMessage.style.display = 'none';
                    }
                }, 5000);
            }
        }
        console.log(`💬 [${type}] ${message}`);
    }

    // ✅ MANEJAR RESTABLECIMIENTO DE CONTRASEÑA
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            console.log('🔄 Reset button clicked');
            
            const otp = otpInput.value.trim();
            const newPassword = newPasswordInput.value;
            const confirmNewPassword = confirmNewPasswordInput.value;
            const email = recoveryEmail;

            // Validaciones
            if (!otp || otp.length !== 6) {
                showMessage('❌ Por favor ingresa el código de 6 dígitos', 'error');
                return;
            }

            if (!newPassword) {
                showMessage('❌ Por favor ingresa una nueva contraseña', 'error');
                return;
            }

            if (newPassword.length !== 10) {
                showMessage('❌ La contraseña debe tener exactamente 10 caracteres', 'error');
                return;
            }

            // ✅ VALIDACIÓN: Verificar que no tenga símbolos
            const hasNoSymbols = /^[a-zA-Z\d]+$/.test(newPassword);
            if (!hasNoSymbols) {
                showMessage("❌ La contraseña no puede contener símbolos especiales (@, ., etc)", 'error');
                return;
            }

            if (!/[A-Z]/.test(newPassword)) {
                showMessage('❌ La contraseña debe contener al menos una letra mayúscula', 'error');
                return;
            }

            if (!/[a-z]/.test(newPassword)) {
                showMessage('❌ La contraseña debe contener al menos una letra minúscula', 'error');
                return;
            }

            if (!/\d/.test(newPassword)) {
                showMessage('❌ La contraseña debe contener al menos un número', 'error');
                return;
            }

            if (newPassword !== confirmNewPassword) {
                showMessage('❌ Las contraseñas no coinciden', 'error');
                return;
            }

            try {
                showMessage('⏳ Verificando código y actualizando contraseña...', 'info');
                resetBtn.classList.add('loading');
                resetBtn.disabled = true;

                console.log('📤 Sending password reset request...');
                
                const response = await fetch(`${API_URL}/api/auth/password-recovery/reset`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ 
                        email,
                        otp,
                        new_password: newPassword
                    })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                if (response.ok) {
                    if (data.success) {
                        showMessage('✅ Contraseña actualizada correctamente. Redirigiendo al login...', 'success');
                        
                        // ✅ LIMPIAR DATOS DE RECUPERACIÓN
                        localStorage.removeItem('recovery_email');
                        localStorage.removeItem('recovery_token');
                        
                        // Redirigir al login después de 3 segundos
                        setTimeout(() => {
                        window.location.href = '/access/log_in/login.html';
                        }, 3000);
                    } else {
                        showMessage('❌ ' + (data.error || 'Error al actualizar la contraseña'), 'error');
                        resetBtn.classList.remove('loading');
                        resetBtn.disabled = false;
                    }
                } else {
                    // Manejar errores específicos
                    if (response.status === 400) {
                        showMessage('❌ Código inválido o expirado', 'error');
                    } else if (response.status === 404) {
                        showMessage('❌ No se encontró la solicitud de recuperación', 'error');
                    } else {
                        showMessage('❌ Error: ' + (data.error || 'Error en el servidor'), 'error');
                    }
                    resetBtn.classList.remove('loading');
                    resetBtn.disabled = false;
                }
            } catch (error) {
                console.error('❌ Error:', error);
                
                if (error.toString().includes('Failed to fetch') || error.toString().includes('CONNECTION_REFUSED')) {
                    showMessage('❌ No se puede conectar al servidor. Verifica tu conexión a internet.', 'error');
                } else {
                    showMessage('❌ Error de conexión: ' + error.message, 'error');
                }
                
                resetBtn.classList.remove('loading');
                resetBtn.disabled = false;
            }
        });
    }

    // Permitir Enter para enviar
    if (otpInput) {
        otpInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && resetBtn && !resetBtn.disabled) {
                resetBtn.click();
            }
        });
    }

    if (newPasswordInput) {
        newPasswordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && resetBtn && !resetBtn.disabled) {
                resetBtn.click();
            }
        });
    }

    if (confirmNewPasswordInput) {
        confirmNewPasswordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && resetBtn && !resetBtn.disabled) {
                resetBtn.click();
            }
        });
    }

    // Auto-focus en el input de OTP
    if (otpInput) {
        otpInput.focus();
    }

    // Limpiar localStorage cuando se cierre la página
    window.addEventListener('beforeunload', () => {
        // Mantener el email por si el usuario regresa
        // Solo limpiar token temporal
        localStorage.removeItem('recovery_token');
    });
});