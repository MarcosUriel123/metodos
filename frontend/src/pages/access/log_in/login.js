document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Login page loaded');

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
    
    
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');
    const emailInput = document.getElementById('email');
    const loginForm = document.getElementById('loginForm');
    const loginMessage = document.getElementById('loginMessage');
    const submitBtn = document.getElementById('submitBtn');

    // Toggle password visibility (sin cambios)
    if (togglePassword) {
        togglePassword.addEventListener('click', () => {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            togglePassword.querySelector('i').classList.toggle('fa-eye');
            togglePassword.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    // Validaciones en tiempo real (sin cambios)
    if (emailInput) {
        emailInput.addEventListener('input', validateEmail);
        emailInput.addEventListener('blur', validateEmail);
    }

    if (password) {
        password.addEventListener('input', validatePassword);
        password.addEventListener('blur', validatePassword);
    }

    // Función para validar email (sin cambios)
    function validateEmail() {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email === '') {
            setInputState(emailInput, 'neutral');
            return false;
        }
        
        if (!emailRegex.test(email)) {
            setInputState(emailInput, 'invalid');
            return false;
        }
        
        setInputState(emailInput, 'valid');
        return true;
    }

    // Función para validar contraseña (sin cambios)
    function validatePassword() {
        const passwordValue = password.value;
        
        if (passwordValue === '') {
            setInputState(password, 'neutral');
            return false;
        }
        
        if (passwordValue.length < 6 || passwordValue.length > 10) {
            setInputState(password, 'invalid');
            return false;
        }
        
        setInputState(password, 'valid');
        return true;
    }

    // Función para establecer estado visual del input (sin cambios)
    function setInputState(inputElement, state) {
        inputElement.classList.remove('valid', 'invalid');
        
        if (state === 'valid') {
            inputElement.classList.add('valid');
        } else if (state === 'invalid') {
            inputElement.classList.add('invalid');
        }
    }

    // Validar formulario completo antes de enviar (sin cambios)
    function validateForm() {
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();
        
        if (!isEmailValid) {
            showMessage('Por favor ingresa un email válido', 'error');
            return false;
        }
        
        if (!isPasswordValid) {
            showMessage('La contraseña debe tener entre 6 y 10 caracteres', 'error');
            return false;
        }
        
        return true;
    }

    // Handle form submission - ACTUALIZADO CON EMAIL OTP
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            console.log('📝 Form submitted');

            if (!validateForm()) {
                return;
            }

            const email = document.getElementById("email").value.trim();
            const passwordValue = document.getElementById("password").value;

            showMessage('Iniciando sesión...', 'info');
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            try {
                console.log('📤 Sending login request...');
                
                    const response = await fetch(`${API_URL}/api/auth/login`, {  // ✅ CAMBIADO
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    credentials: "include",
                    body: JSON.stringify({ email: email, password: passwordValue })
                });

                console.log('📨 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                if (response.ok && data.success) {
                    // ✅ GUARDAR EMAIL EN LOCALSTORAGE PARA TODOS LOS MÉTODOS
                    localStorage.setItem('user_email', email);
                    
                    // ✅ OBTENER Y GUARDAR FIRST_NAME
                    try {
                        console.log('📡 Obteniendo información del usuario para first_name...');
                        let userInfoEndpoint;
                        
                        // ✅ NUEVO: Determinar endpoint según método de autenticación
                        if (data.auth_method === 'sms') {
                            userInfoEndpoint = `${API_URL}/api/auth/sms/user-info?email=${encodeURIComponent(email)}`;  // ✅ CAMBIADO
                        } else if (data.auth_method === 'email') {
                            userInfoEndpoint = `${API_URL}/api/auth/email/user-info?email=${encodeURIComponent(email)}`;  // ✅ CAMBIADO
                        } else {
                            userInfoEndpoint = `${API_URL}/api/auth/totp/user-info?email=${encodeURIComponent(email)}`;  // ✅ CAMBIADO
                        }
                        
                        const userInfoResponse = await fetch(userInfoEndpoint, {
                            method: 'GET',
                            credentials: 'include'
                        });
                        
                        if (userInfoResponse.ok) {
                            const userData = await userInfoResponse.json();
                            if (userData.first_name) {
                                localStorage.setItem('user_first_name', userData.first_name);
                                console.log('✅ First name guardado:', userData.first_name);
                            }
                        }
                    } catch (error) {
                        console.log('ℹ️ Error obteniendo first_name:', error);
                    }
                    
                    if (data.requires_otp) {
                        // ✅ GUARDAR EN MÚLTIPLES LUGARES
                        localStorage.setItem('pending_verification_email', email);
                        localStorage.setItem('user_email', email);
                        sessionStorage.setItem('verification_email', email);
                        
                        showMessage('Redirigiendo a verificación...', 'success');
                        
                        setTimeout(() => {
                            // ✅ NUEVO: Manejar redirección para Email OTP
                            if (data.auth_method === 'email') {
                                console.log('✅ Redirigiendo a verificación EMAIL con email:', email);
                                window.location.href = "../../auth-methods/email/verification/email_verification.html";
                            } 
                            // Manejar SMS (existente)
                            else if (data.auth_method === 'sms') {
                                handleSmsLogin(email).then(() => {
                                    console.log('✅ Redirigiendo a verificación SMS con email:', email);
                                    window.location.href = "../../auth-methods/sms-otp/verification/verification.html";
                                });
                            } 
                            // Manejar TOTP (existente)
                            else {
                                window.location.href = "../../auth-methods/totp/verification/verification.html";
                            }
                        }, 1000);
                    } else {
                        // Login directo sin OTP
                        showMessage('✅ Login exitoso. Redirigiendo...', 'success');
                        
                        localStorage.removeItem('pending_verification_email');
                        sessionStorage.removeItem('verification_email');
                        
                        setTimeout(() => {
                            window.location.href = "../../index/index.html";
                        }, 1000);
                    }
                } else {
                    // Manejar errores (sin cambios)
                    if (response.status === 401) {
                        if (data.error && data.error.includes('no registrado')) {
                            showMessage('❌ El correo electrónico no está registrado', 'error');
                        } else if (data.error && data.error.includes('contraseña')) {
                            showMessage('❌ Contraseña incorrecta', 'error');
                        } else {
                            showMessage('❌ Credenciales inválidas', 'error');
                        }
                    } else if (response.status === 404) {
                        showMessage('❌ El usuario no existe', 'error');
                    } else if (response.status === 400) {
                        showMessage('❌ Datos de entrada inválidos', 'error');
                    } else {
                        showMessage(data.error || "Error al iniciar sesión", 'error');
                    }
                    
                    password.value = '';
                    validatePassword();
                }
            } catch (error) {
                console.error('❌ Error:', error);
                showMessage("❌ Error de conexión con el servidor", 'error');
            } finally {
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
            }
        });
    }

    // ✅ FUNCIÓN MEJORADA: Configurar sesión SMS (sin cambios)
    async function handleSmsLogin(email) {
        try {
            console.log('📱 Configurando sesión SMS para:', email);
            
            const userResponse = await fetch(`${API_URL}/api/auth/sms/user-info?email=${encodeURIComponent(email)}`, {  // ✅ CAMBIADO
                method: 'GET',
                credentials: 'include'
            });

            if (userResponse.ok) {
                const userData = await userResponse.json();
                const phoneNumber = userData.phone_number;
                
                console.log('📞 Teléfono del usuario:', phoneNumber);
                
                if (phoneNumber) {
                    sessionStorage.setItem('user_phone', phoneNumber);
                    sessionStorage.setItem('user_email', email);
                    localStorage.setItem('user_phone', phoneNumber);
                }
            }
        } catch (error) {
            console.error('❌ Error en handleSmsLogin:', error);
        }
    }

    function showMessage(message, type) {
        if (loginMessage) {
            loginMessage.textContent = message;
            loginMessage.className = `login-message message-${type}`;
            loginMessage.style.display = 'block';
            
            loginMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            if (type !== 'success') {
                setTimeout(() => {
                    if (loginMessage.textContent === message) {
                        loginMessage.style.display = 'none';
                    }
                }, 5000);
            }
        }
        console.log(`💬 [${type}] ${message}`);
    }

    // Limpiar mensajes cuando el usuario empiece a escribir (sin cambios)
    if (emailInput) {
        emailInput.addEventListener('input', () => {
            if (loginMessage.style.display === 'block') {
                loginMessage.style.display = 'none';
            }
            emailInput.classList.remove('invalid');
        });
    }

    if (password) {
        password.addEventListener('input', () => {
            if (loginMessage.style.display === 'block') {
                loginMessage.style.display = 'none';
            }
            password.classList.remove('invalid');
        });
    }

    // ✅ VERIFICAR SI HAY UNA SESIÓN ACTIVA AL CARGAR LA PÁGINA (sin cambios)
    const userEmail = localStorage.getItem('user_email');
    if (userEmail) {
        console.log('✅ Sesión activa encontrada:', userEmail);
    }
});