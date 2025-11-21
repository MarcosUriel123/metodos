document.addEventListener('DOMContentLoaded', () => {
    console.log('📧 Email OTP page loaded');

    // ✅ VERSIÓN DEFINITIVA - COPIAR EN TODOS LOS JS
    const API_URL = (() => {
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || 
            hostname === '127.0.0.1' ||
            window.location.port !== '') {
            return 'http://localhost:5000';
        } else {
            return 'https://metodos-scwr.onrender.com';
        }
    })();
    
    const emailForm = document.getElementById('emailForm');
    const emailInput = document.getElementById('email');
    const submitBtn = document.getElementById('submitBtn');
    const emailMessage = document.getElementById('emailMessage');

    // Función para mostrar mensajes
    function showMessage(message, type) {
        if (emailMessage) {
            emailMessage.textContent = message;
            emailMessage.className = `email-message message-${type}`;
            emailMessage.style.display = 'block';
            
            // Scroll to message
            emailMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Auto-ocultar mensajes después de 5 segundos (excepto success)
            if (type !== 'success') {
                setTimeout(() => {
                    if (emailMessage.textContent === message) {
                        emailMessage.style.display = 'none';
                    }
                }, 5000);
            }
        }
        console.log(`💬 [${type}] ${message}`);
    }

    // Función para validar email
    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Manejar envío del formulario
    if (emailForm) {
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = emailInput.value.trim();
            
            // Validaciones
            if (!email) {
                showMessage('❌ Por favor ingresa un correo electrónico', 'error');
                return;
            }
            
            if (!validateEmail(email)) {
                showMessage('❌ Por favor ingresa un correo electrónico válido', 'error');
                return;
            }

            try {
                showMessage('⏳ Enviando código de verificación...', 'info');
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;

                console.log('📤 Enviando solicitud de OTP por email...');
                
                const response = await fetch(`${API_URL}/api/auth/email/send-otp`, {  // ✅ CAMBIADO
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

                if (response.ok && data.success) {
                    showMessage('✅ Código enviado exitosamente. Redirigiendo...', 'success');
                    
                    // Guardar email en localStorage para la verificación
                    localStorage.setItem('pending_verification_email', email);
                    localStorage.setItem('user_email', email);
                    
                    // Redirigir a la página de verificación después de 2 segundos
                    setTimeout(() => {
                        window.location.href = 'verification/email_verification.html';
                    }, 2000);
                } else {
                    showMessage('❌ Error: ' + (data.error || 'No se pudo enviar el código'), 'error');
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage('❌ Error de conexión con el servidor', 'error');
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
            }
        });
    }

    // Pre-llenar email si está disponible en localStorage
    const savedEmail = localStorage.getItem('user_email') || localStorage.getItem('pending_verification_email');
    if (savedEmail && emailInput) {
        emailInput.value = savedEmail;
        console.log('✅ Email pre-llenado:', savedEmail);
    }

    // Limpiar mensajes cuando el usuario empiece a escribir
    if (emailInput) {
        emailInput.addEventListener('input', () => {
            if (emailMessage.style.display === 'block') {
                emailMessage.style.display = 'none';
            }
        });
    }
});