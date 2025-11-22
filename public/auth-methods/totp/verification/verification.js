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
  
var value = ""
const btn_submt = document.querySelector('.submit_btn');
btn_submt.disabled = true
const inputs = Array.from(document.querySelectorAll('input[class^="form-control"]'));

// ✅ VERIFICAR EMAIL AL CARGAR LA PÁGINA
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 TOTP Verification page loaded');
    
    const userEmail = localStorage.getItem('user_email') || 
                     localStorage.getItem('pending_verification_email');
    
    if (!userEmail) {
        console.error('❌ No se encontró email en localStorage');
        alert('❌ No se encontró información del usuario. Regresa al login.');
        setTimeout(() => {
            window.location.href = "../../access/log_in/login.html";
        }, 2000);
        return;
    }
    
    console.log('✅ Email encontrado para verificación TOTP:', userEmail);
});

inputs.forEach((input, idx) => {
    input.setAttribute('maxlength', 1);

    input.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
        updateValue();
        if (e.target.value.length === 1 && idx < inputs.length - 1) {
            inputs[idx + 1].focus();
        }
        subIsActive();
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && e.target.value === '' && idx > 0) {
            inputs[idx - 1].focus();
        }
        setTimeout(() => {
            updateValue();
            subIsActive();
        }, 0);
    });
});

function subIsActive() {
    const filled = inputs.filter(input => input.value.length === 1).length;
    btn_submt.disabled = filled !== 6;
}

function updateValue() {
    value = inputs.map(input => input.value).join('');
}

btn_submt.addEventListener('click', () => {
    const otpCode = inputs.map(input => input.value).join('');
    
    // ✅ OBTENER EMAIL DE MULTIPLES FUENTES
    const userEmail = localStorage.getItem('user_email') || 
                     localStorage.getItem('pending_verification_email');
    
    if (!userEmail) {
        alert('❌ No se encontró información del usuario. Por favor regresa al login.');
        return;
    }

    console.log('🔐 Verificando TOTP para:', userEmail, 'Código:', otpCode);

    // Deshabilitar botón durante la verificación
    btn_submt.disabled = true;
    btn_submt.textContent = 'Verificando...';

    fetch(`${API_URL}/api/auth/totp/verify`, {  // ✅ CAMBIADO
        method: 'POST',
        credentials: 'include',      
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            email: userEmail,
            code: otpCode 
        })
    })
    .then(response => {
        console.log('📨 Status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📦 Response:', data);
        
        if (data.valid) {
            alert('✅ Código verificado correctamente');
            
            // Establecer la sesión antes de redirigir
            localStorage.setItem('auth_method', 'totp');
            localStorage.setItem('isAuthenticated', 'true');
            localStorage.setItem('user_email', userEmail);
            
            // Limpiar email temporal
            localStorage.removeItem('pending_verification_email');
            
            // Redirigir al index
            setTimeout(() => {
                window.location.href = "../../../index.html";
            }, 1000);
        } else {
            alert('❌ Código OTP inválido o expirado');
            // Limpiar inputs para nuevo intento
            inputs.forEach(input => input.value = '');
            inputs[0].focus();
            btn_submt.disabled = false;
            btn_submt.textContent = 'Verificar';
            subIsActive();
        }
    })
    .catch(error => {
        console.error('❌ Error al validar OTP:', error);
        alert('❌ Error de conexión con el servidor');
        btn_submt.disabled = false;
        btn_submt.textContent = 'Verificar';
    });
});

// ✅ Permitir Enter para enviar
inputs[inputs.length - 1]?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !btn_submt.disabled) {
        btn_submt.click();
    }
});