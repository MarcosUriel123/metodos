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
    console.log('🔐 Password Recovery Request page loaded');
    
    // Elementos del DOM
    const recoveryForm = document.getElementById('recoveryForm');
    const recoveryBtn = document.getElementById('recoveryBtn');
    const emailInput = document.getElementById('email');
    const recoveryMessage = document.getElementById('recoveryMessage');

    // ✅ VALIDACIÓN: Bloquear símbolos especiales en email
    if (emailInput) {
        emailInput.addEventListener('input', (e) => {
            // Permitir solo: letras, números, @, ., _, %, +, -
            let value = e.target.value;
            value = value.replace(/[^a-zA-Z0-9@._%+-]/g, '');
            
            // Limitar a 100 caracteres
            if (value.length > 100) {
                value = value.substring(0, 100);
            }
            
            e.target.value = value;
        });
    }

    // Función para mostrar mensajes
    function showMessage(message, type) {
        if (recoveryMessage) {
            recoveryMessage.textContent = message;
            recoveryMessage.className = `recovery-message message-${type}`;
            recoveryMessage.style.display = 'block';
            
            recoveryMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            if (type !== 'success') {
                setTimeout(() => {
                    if (recoveryMessage.textContent === message) {
                        recoveryMessage.style.display = 'none';
                    }
                }, 5000);
            }
        }
        console.log(`💬 [${type}] ${message}`);
    }

    // ✅ MANEJAR SOLICITUD DE RECUPERACIÓN
    if (recoveryBtn) {
        recoveryBtn.addEventListener('click', async () => {
            console.log('📧 Recovery button clicked');
            
            const email = emailInput.value.trim();
            
            // Validaciones básicas
            if (!email) {
                showMessage('❌ Por favor ingresa tu correo electrónico', 'error');
                return;
            }

            if (!email.includes('@') || !email.includes('.')) {
                showMessage('❌ Por favor ingresa un correo electrónico válido', 'error');
                return;
            }

            try {
                showMessage('⏳ Verificando tu correo y enviando código...', 'info');
                recoveryBtn.classList.add('loading');
                recoveryBtn.disabled = true;

                console.log('📤 Sending recovery request...');
                
                const response = await fetch(`${API_URL}/api/auth/password-recovery/request`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ email })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                if (response.ok) {
                    if (data.success) {
                        showMessage('✅ Código enviado correctamente. Revisa tu correo electrónico. Redirigiendo...', 'success');
                        
                        // ✅ GUARDAR EMAIL PARA LA SIGUIENTE PANTALLA
                        localStorage.setItem('recovery_email', email);
                        localStorage.setItem('recovery_token', data.recovery_token || 'temp_token');
                        
                        console.log('✅ Email guardado para recuperación:', email);
                        
                        // Redirigir a la página de restablecimiento después de 2 segundos
                        setTimeout(() => {
                            window.location.href = '../reset/reset.html';
                        }, 2000);
                    } else {
                        showMessage('❌ ' + (data.error || 'Error al enviar el código'), 'error');
                        recoveryBtn.classList.remove('loading');
                        recoveryBtn.disabled = false;
                    }
                } else {
                    // Manejar errores específicos
                    if (response.status === 404) {
                        showMessage('❌ No existe una cuenta con este correo electrónico', 'error');
                    } else if (response.status === 429) {
                        showMessage('❌ Demasiados intentos. Espera 10 minutos antes de intentar nuevamente', 'error');
                    } else {
                        showMessage('❌ Error: ' + (data.error || 'Error en el servidor'), 'error');
                    }
                    recoveryBtn.classList.remove('loading');
                    recoveryBtn.disabled = false;
                }
            } catch (error) {
                console.error('❌ Error:', error);
                
                if (error.toString().includes('Failed to fetch') || error.toString().includes('CONNECTION_REFUSED')) {
                    showMessage('❌ No se puede conectar al servidor. Verifica tu conexión a internet.', 'error');
                } else {
                    showMessage('❌ Error de conexión: ' + error.message, 'error');
                }
                
                recoveryBtn.classList.remove('loading');
                recoveryBtn.disabled = false;
            }
        });
    }

    // Permitir Enter para enviar
    if (emailInput) {
        emailInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && recoveryBtn && !recoveryBtn.disabled) {
                recoveryBtn.click();
            }
        });
    }

    // Auto-focus en el input de email
    if (emailInput) {
        emailInput.focus();
    }

    // Verificar si ya hay un email en localStorage (por si el usuario regresa)
    const existingRecoveryEmail = localStorage.getItem('recovery_email');
    if (existingRecoveryEmail) {
        console.log('📧 Email de recuperación encontrado en localStorage:', existingRecoveryEmail);
        emailInput.value = existingRecoveryEmail;
    }

    // Limpiar localStorage cuando se cierre la página (solo el token, mantener email)
    window.addEventListener('beforeunload', () => {
        localStorage.removeItem('recovery_token');
    });
});