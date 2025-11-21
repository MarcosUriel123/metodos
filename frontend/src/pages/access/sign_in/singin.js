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
        return 'https://auth-backend.onrender.com';
    }
})();

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Sign in page loaded');
    // ... resto de tu código ...
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Sign in page loaded');
    
    // Elementos del DOM
    const togglePassword = document.getElementById('togglePassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const authMethodQR = document.getElementById('authMethodQR');
    const authMethodSMS = document.getElementById('authMethodSMS');
    const authMethodEmail = document.getElementById('authMethodEmail');
    const phoneNumberField = document.getElementById('phoneNumberField');
    const phoneNumberInput = document.getElementById('phone_number');
    const registerMessage = document.getElementById('registerMessage');
    const firstNameInput = document.getElementById('first_name');
    const lastNameInput = document.getElementById('last_name');

    // ✅ VALIDACIÓN: Solo permitir números en teléfono
    if (phoneNumberInput) {
        phoneNumberInput.addEventListener('input', (e) => {
            // Permitir solo números y el símbolo + al inicio
            let value = e.target.value;
            
            // Si empieza con +52, permitirlo
            if (value.startsWith('+52')) {
                value = '+52' + value.slice(3).replace(/\D/g, '');
            } else {
                // Solo números
                value = value.replace(/\D/g, '');
            }
            
            e.target.value = value;
        });
    }

    // ✅ VALIDACIÓN: Solo letras en nombres y apellidos
    function validateNameInput(input) {
        input.addEventListener('input', (e) => {
            // Permitir solo letras, espacios y caracteres especiales del español
            let value = e.target.value;
            value = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]/g, '');
            
            // Limitar a 45 caracteres
            if (value.length > 45) {
                value = value.substring(0, 45);
            }
            
            e.target.value = value;
        });
    }

    if (firstNameInput) validateNameInput(firstNameInput);
    if (lastNameInput) validateNameInput(lastNameInput);

    // ✅ VALIDACIÓN: Contraseña en tiempo real
    if (password) {
        password.addEventListener('input', (e) => {
            const value = e.target.value;
            const passwordHint = document.querySelector('.password-hint');
            
            // Validar requisitos
            const hasUpperCase = /[A-Z]/.test(value);
            const hasLowerCase = /[a-z]/.test(value);
            const hasNumber = /\d/.test(value);
            const isValidLength = value.length === 10;
            
            // Actualizar hint con colores
            if (passwordHint) {
                let hintText = '';
                
                if (!isValidLength) {
                    hintText = `${value.length}/10 caracteres`;
                } else if (!hasUpperCase || !hasLowerCase || !hasNumber) {
                    hintText = 'Falta: ';
                    if (!hasUpperCase) hintText += 'mayúscula ';
                    if (!hasLowerCase) hintText += 'minúscula ';
                    if (!hasNumber) hintText += 'número';
                } else {
                    hintText = '✅ Contraseña válida';
                    passwordHint.style.color = '#10b981';
                }
                
                if (!isValidLength || !hasUpperCase || !hasLowerCase || !hasNumber) {
                    passwordHint.style.color = '#ef4444';
                }
                
                passwordHint.textContent = hintText;
            }
        });
    }

    // Función para formatear número de teléfono
    function formatPhoneNumber(phone) {
        const cleaned = phone.replace(/\D/g, '');
        
        if (cleaned.startsWith('52') && cleaned.length === 12) {
            return `+${cleaned}`;
        }
        
        if (cleaned.length === 10) {
            return `+52${cleaned}`;
        }
        
        if (cleaned.startsWith('52') && phone.startsWith('+')) {
            return phone;
        }
        
        return cleaned;
    }

    // Función para validar formato de teléfono
    function isValidPhoneNumber(phone) {
        const cleaned = phone.replace(/\D/g, '');
        
        return (cleaned.length === 10) || 
               (cleaned.length === 12 && cleaned.startsWith('52')) ||
               (phone.startsWith('+52') && cleaned.length === 12);
    }

    // Función para mostrar mensajes
    function showMessage(message, type) {
        if (registerMessage) {
            registerMessage.textContent = message;
            registerMessage.className = `register-message message-${type}`;
            registerMessage.style.display = 'block';
            
            registerMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            if (type !== 'success') {
                setTimeout(() => {
                    if (registerMessage.textContent === message) {
                        registerMessage.style.display = 'none';
                    }
                }, 5000);
            }
        }
        console.log(`💬 [${type}] ${message}`);
    }

    // Manejar cambio de método de autenticación
    function togglePhoneField() {
        const selectedMethod = document.querySelector('input[name="authMethod"]:checked');
        
        if (selectedMethod && selectedMethod.value === 'sms') {
            phoneNumberField.style.display = 'block';
            phoneNumberInput.setAttribute('required', 'true');
            console.log('📱 Campo de teléfono mostrado');
        } else {
            phoneNumberField.style.display = 'none';
            phoneNumberInput.removeAttribute('required');
            phoneNumberInput.value = '';
            console.log('📱 Campo de teléfono ocultado');
        }
    }

    // Agregar event listeners a los radio buttons
    if (authMethodQR && authMethodSMS && authMethodEmail) {
        authMethodQR.addEventListener('change', togglePhoneField);
        authMethodSMS.addEventListener('change', togglePhoneField);
        authMethodEmail.addEventListener('change', togglePhoneField);
        console.log('✅ Event listeners para métodos de autenticación agregados');
    }

    // Toggle password visibility
    if (togglePassword) {
        togglePassword.addEventListener('click', () => {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            const icon = togglePassword.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }

    if (toggleConfirmPassword) {
        toggleConfirmPassword.addEventListener('click', () => {
            const type = confirmPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmPassword.setAttribute('type', type);
            const icon = toggleConfirmPassword.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }

    // También manejar los clics en las etiquetas de los métodos
    document.querySelectorAll('.method-option').forEach(option => {
        option.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                togglePhoneField();
            }
        });
    });

    // Inicializar el estado del campo de teléfono
    togglePhoneField();
});

document.getElementById("registerBtn").addEventListener("click", async () => {
    console.log('📝 Register button clicked');
    
    const first_name = document.getElementById("first_name").value.trim();
    const last_name = document.getElementById("last_name").value.trim();
    const email = document.getElementById("your_email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const authMethodElement = document.querySelector('input[name="authMethod"]:checked');
    let phone_number = document.getElementById("phone_number").value.trim();
    const registerMessage = document.getElementById('registerMessage');
    const registerBtn = document.getElementById('registerBtn');

    // Función para formatear número de teléfono
    function formatPhoneNumber(phone) {
        const cleaned = phone.replace(/\D/g, '');
        
        if (cleaned.startsWith('52') && cleaned.length === 12) {
            return `+${cleaned}`;
        }
        
        if (cleaned.length === 10) {
            return `+52${cleaned}`;
        }
        
        if (cleaned.startsWith('52') && phone.startsWith('+')) {
            return phone;
        }
        
        return cleaned;
    }

    // Función para validar formato de teléfono
    function isValidPhoneNumber(phone) {
        const cleaned = phone.replace(/\D/g, '');
        
        return (cleaned.length === 10) || 
               (cleaned.length === 12 && cleaned.startsWith('52')) ||
               (phone.startsWith('+52') && cleaned.length === 12);
    }

    // Función para mostrar mensajes
    function showMessage(message, type) {
        if (registerMessage) {
            registerMessage.textContent = message;
            registerMessage.className = `register-message message-${type}`;
            registerMessage.style.display = 'block';
            
            registerMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            if (type !== 'success') {
                setTimeout(() => {
                    if (registerMessage.textContent === message) {
                        registerMessage.style.display = 'none';
                    }
                }, 5000);
            }
        }
        console.log(`💬 [${type}] ${message}`);
    }

    // ✅ VALIDACIONES MEJORADAS
    if (!first_name) {
        showMessage("❌ Por favor ingresa tu nombre.", 'error');
        return;
    }

    if (first_name.length > 45) {
        showMessage("❌ El nombre no puede exceder 45 caracteres.", 'error');
        return;
    }

    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(first_name)) {
        showMessage("❌ El nombre solo puede contener letras.", 'error');
        return;
    }

    if (!last_name) {
        showMessage("❌ Por favor ingresa tu apellido.", 'error');
        return;
    }

    if (last_name.length > 45) {
        showMessage("❌ El apellido no puede exceder 45 caracteres.", 'error');
        return;
    }

    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(last_name)) {
        showMessage("❌ El apellido solo puede contener letras.", 'error');
        return;
    }

    if (!email || !email.includes("@")) {
        showMessage("❌ Por favor ingresa un correo válido.", 'error');
        return;
    }

    // ✅ VALIDACIÓN DE CONTRASEÑA MEJORADA
    if (!password) {
        showMessage("❌ Por favor ingresa una contraseña.", 'error');
        return;
    }

    if (password.length !== 10) {
        showMessage("❌ La contraseña debe tener exactamente 10 caracteres.", 'error');
        return;
    }

    if (!/[A-Z]/.test(password)) {
        showMessage("❌ La contraseña debe contener al menos una letra mayúscula.", 'error');
        return;
    }

    if (!/[a-z]/.test(password)) {
        showMessage("❌ La contraseña debe contener al menos una letra minúscula.", 'error');
        return;
    }

    if (!/\d/.test(password)) {
        showMessage("❌ La contraseña debe contener al menos un número.", 'error');
        return;
    }

    if (password !== confirmPassword) {
        showMessage("❌ Las contraseñas no coinciden.", 'error');
        return;
    }

    if (!authMethodElement) {
        showMessage("❌ Por favor selecciona un método de autenticación.", 'error');
        return;
    }

    const authMethod = authMethodElement.value;

    // Validación específica para SMS
    if (authMethod === 'sms') {
        if (!phone_number) {
            showMessage("❌ Por favor ingresa un número de teléfono.", 'error');
            return;
        }

        if (!isValidPhoneNumber(phone_number)) {
            showMessage("❌ Formato de teléfono inválido. Usa 10 dígitos (ej: 5512345678) o +52 seguido de 10 dígitos.", 'error');
            return;
        }

        phone_number = formatPhoneNumber(phone_number);
        console.log(`📞 Número formateado para Twilio: ${phone_number}`);
    }

    try {
        showMessage('⏳ Registrando usuario...', 'info');
        registerBtn.classList.add('loading');
        registerBtn.disabled = true;

        console.log('📤 Sending registration request...');
        
        const url = `${API_URL}/api/auth/register`;  // ✅ SOLO CAMBIAR ESTA LÍNEA
        
        console.log(`🎯 Using URL: ${url} for auth method: ${authMethod}`);
        console.log(`📞 Phone number: ${phone_number}`);

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include", 
            body: JSON.stringify({ 
                email, 
                password, 
                first_name, 
                last_name,
                auth_method: authMethod,
                phone_number: authMethod === 'sms' ? phone_number : null
            })
        });

        console.log('📨 Response status:', response.status);
        
        const data = await response.json();
        console.log('📦 Response data:', data);

        if (response.ok) {
            // ✅ GUARDAR EMAIL Y FIRST_NAME EN LOCALSTORAGE
            localStorage.setItem('user_email', email);
            localStorage.setItem('user_first_name', first_name);
            
            console.log('✅ Datos guardados en localStorage:', { email, first_name });
            
            // Manejar redirección para Email OTP
            if (authMethod === 'email') {
                if (data.success && data.requires_otp) {
                    showMessage("✅ Usuario registrado correctamente. Se envió un código por email. Redirigiendo...", 'success');
                    
                    localStorage.setItem('pending_verification_email', email);
                    
                    setTimeout(() => {
                        window.location.href = "../../auth-methods/email/verification/email_verification.html";
                    }, 2000);
                } else {
                    showMessage("⚠️ Usuario registrado. Si no recibes el email, usa 'Reenviar código'. Redirigiendo...", 'warning');
                    
                    localStorage.setItem('pending_verification_email', email);
                    
                    setTimeout(() => {
                        window.location.href = "../../auth-methods/email/verification/email_verification.html";
                    }, 2000);
                }
            }
            // Manejar SMS
            else if (authMethod === 'sms') {
                if (data.success && data.requires_otp) {
                    showMessage("✅ Usuario registrado correctamente. Se envió un código por SMS. Redirigiendo...", 'success');
                    
                    localStorage.setItem('pending_verification_email', email);
                    
                    setTimeout(() => {
                        window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                    }, 2000);
                } else {
                    showMessage("⚠️ Usuario registrado. Si no recibes el SMS, usa 'Reenviar código'. Redirigiendo...", 'warning');
                    
                    localStorage.setItem('pending_verification_email', email);
                    
                    setTimeout(() => {
                        window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                    }, 2000);
                }
            } 
            // Manejar TOTP
            else {
                showMessage("✅ Usuario registrado correctamente. Escanea el QR en la app de autenticación. Redirigiendo...", 'success');
                
                setTimeout(() => {
                    window.location.href = "../../auth-methods/totp/qr_scan/qr.html";
                }, 2000);
            }
        } else {
            if (response.status === 500 && data.error === 'Failed to send OTP') {
                showMessage("⚠️ Usuario registrado. Si no recibes el código, usa 'Reenviar código'. Redirigiendo...", 'warning');
                localStorage.setItem('pending_verification_email', email);
                
                const redirectPath = authMethod === 'email' 
                    ? "../../auth-methods/email/verification/email_verification.html"
                    : "../../auth-methods/sms-otp/verification/verification.html";
                
                setTimeout(() => {
                    window.location.href = redirectPath;
                }, 2000);
            } else {
                showMessage("❌ Error: " + (data.error || 'Error en el registro'), 'error');
                registerBtn.classList.remove('loading');
                registerBtn.disabled = false;
            }
        }
    } catch (error) {
        console.error('❌ Error:', error);
        
        if (error.toString().includes('Failed to fetch') || error.toString().includes('CONNECTION_REFUSED')) {
            showMessage("❌ No se puede conectar al servidor. Verifica que el backend esté ejecutándose en puerto 5000.", 'error');
        } else {
            showMessage("❌ Error al conectar con el servidor: " + error.message, 'error');
        }
        
        registerBtn.classList.remove('loading');
        registerBtn.disabled = false;
    }
});