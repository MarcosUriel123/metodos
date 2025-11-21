// ✅ VERSIÓN DEFINITIVA - COPIAR EN TODOS LOS JS
const API_URL = (() => {
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || 
        hostname === '127.0.0.1' ||
        window.location.port !== '') {
        return 'http://localhost:5000';
    } else {
        return 'https://auth-backend.onrender.com';
    }
})();

async function cerrarSesion() {
    try {
        // Limpiar TODO el almacenamiento local
        localStorage.removeItem('auth_method');
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('user_email');
        localStorage.removeItem('pending_verification_email');
        localStorage.removeItem('user_first_name');
        
        // ✅ Cerrar sesión en el backend
        try {
            await fetch(`${API_URL}/api/auth/logout`, {  // ✅ CAMBIADO
                method: 'POST',
                credentials: 'include'
            });
            console.log('✅ Logout backend exitoso');
        } catch (e) {
            console.log('ℹ️ Logout backend falló, continuando...');
        }
    } catch (e) {
        console.error('Error en logout:', e);
    }
    
    // Redirigir al login
    window.location.replace('../access/log_in/login.html');
}

async function cargarUsuario() {
    try {
        const authMethod = localStorage.getItem('auth_method');
        const isAuthenticated = localStorage.getItem('isAuthenticated');
        const userEmail = localStorage.getItem('user_email');

        console.log('🔍 Estado auth:', { authMethod, isAuthenticated, userEmail });

        if (!isAuthenticated) {
            console.log('❌ No está autenticado, redirigiendo a login...');
            window.location.replace('../access/log_in/login.html');
            return;
        }

        // ✅ MOSTRAR BIENVENIDA
        console.log('✅ Usuario autenticado, mostrando bienvenida...');
        
        const welcomeText = document.getElementById('welcome-text');
        if (welcomeText) {
            // Intentar usar el nombre guardado primero
            const storedFirstName = localStorage.getItem('user_first_name');
            if (storedFirstName) {
                welcomeText.textContent = `¡Bienvenido ${storedFirstName}!`;
            } else if (userEmail) {
                welcomeText.textContent = `¡Bienvenido ${userEmail}!`;
            } else {
                welcomeText.textContent = '¡Bienvenido Usuario!';
            }
        }

        // ✅ OBTENER INFORMACIÓN DEL USUARIO SEGÚN SU MÉTODO - CORREGIDO PARA EMAIL
        if (userEmail) {
            try {
                console.log('📡 Obteniendo información adicional del usuario...');
                
                let userInfoEndpoint;
                // ✅ NUEVO: Manejar endpoint para Email OTP
                if (authMethod === 'sms') {
                    userInfoEndpoint = `${API_URL}/api/auth/sms/user-info?email=${encodeURIComponent(userEmail)}`;  // ✅ CAMBIADO
                } else if (authMethod === 'email') {
                    userInfoEndpoint = `${API_URL}/api/auth/email/user-info?email=${encodeURIComponent(userEmail)}`;  // ✅ CAMBIADO
                } else {
                    userInfoEndpoint = `${API_URL}/api/auth/totp/user-info?email=${encodeURIComponent(userEmail)}`;  // ✅ CAMBIADO
                }
                
                const response = await fetch(userInfoEndpoint, {
                    credentials: 'include'
                });
                
                if (response.ok) {
                    const userData = await response.json();
                    console.log('📦 Datos usuario:', userData);
                    
                    // ✅ GUARDAR FIRST_NAME EN LOCALSTORAGE
                    if (userData.first_name) {
                        localStorage.setItem('user_first_name', userData.first_name);
                    }
                    
                    // ✅ ACTUALIZAR BIENVENIDA CON NOMBRE
                    if (welcomeText && userData.first_name) {
                        welcomeText.textContent = `¡Bienvenido ${userData.first_name}!`;
                    }
                } else {
                    console.log('ℹ️ Info adicional no disponible, usando datos básicos');
                }
            } catch (e) {
                console.log('ℹ️ Error obteniendo info adicional, usando datos básicos');
            }
        }

    } catch (error) {
        console.error('❌ Error general:', error);
        window.location.replace('../access/log_in/login.html');
    }
}

// ✅ EJECUTAR AL CARGAR LA PÁGINA
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Página de bienvenida cargada');
    cargarUsuario();
});