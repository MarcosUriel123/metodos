document.addEventListener('DOMContentLoaded', () => {
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

    const phoneInput = document.getElementById('phone');
    const smsForm = document.getElementById('smsForm');
    const messageDiv = document.getElementById('message');

    // Verificar que los elementos existen
    if (!smsForm) {
        console.error('❌ No se encontró el formulario con id "smsForm"');
        return;
    }

    if (!phoneInput) {
        console.error('❌ No se encontró el input con id "phone"');
        return;
    }

    if (!messageDiv) {
        console.error('❌ No se encontró el div con id "message"');
        return;
    }

    console.log('✅ Elementos del formulario cargados correctamente');

    // Escuchar el evento submit del formulario
    smsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const phoneNumber = phoneInput.value.trim();
        
        if (!phoneNumber) {
            showMessage('Por favor ingresa un número de teléfono', 'error');
            return;
        }

        try {
            console.log('📤 Enviando solicitud de SMS-LOGIN para:', phoneNumber);
            
            // ✅ USAR ENDPOINT SMS-LOGIN QUE YA ENVÍA EL OTP
            const response = await fetch(`${API_URL}/api/auth/sms-login`, {  // ✅ CAMBIADO
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ phone_number: phoneNumber })
            });

            console.log('📨 Respuesta recibida, status:', response.status);
            const data = await response.json();
            console.log('📦 Datos de respuesta:', data);

            if (response.ok && data.success) {
                // ✅ GUARDAR EMAILS EN LOCALSTORAGE
                if (data.email) {
                    localStorage.setItem('pending_verification_email', data.email);
                    localStorage.setItem('user_email', data.email);
                    console.log('✅ Emails guardados en localStorage:', data.email);
                } else {
                    console.error('❌ No se recibió email en la respuesta');
                    showMessage('Error: No se recibió información del usuario', 'error');
                    return;
                }
                
                showMessage('✅ Código enviado correctamente', 'success');
                
                // Redirigir a la página de verificación
                setTimeout(() => {
                    console.log('🔄 Redirigiendo a verificación...');
                    window.location.href = './verification/verification.html';
                }, 1500);
            } else {
                showMessage(data.error || '❌ Error al enviar el código', 'error');
            }
        } catch (error) {
            console.error('❌ Error de conexión:', error);
            showMessage('❌ Error de conexión con el servidor', 'error');
        }
    });

    function showMessage(text, type) {
        if (messageDiv) {
            messageDiv.textContent = text;
            messageDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} mt-3`;
        }
        console.log(`💬 [${type}] ${text}`);
    } 
});