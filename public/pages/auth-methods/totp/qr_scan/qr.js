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

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("qrContainer");
    
    // ✅ OBTENER EMAIL REAL del localStorage o session
    const userEmail = localStorage.getItem('user_email') || 
                     sessionStorage.getItem('user_email') || 
                     'user@example.com'; // fallback
    
    console.log('📧 Email para QR:', userEmail);
    
    // Evitar cargar múltiples veces
    if (container.querySelector("img")) return;

    try {
        // ✅ USAR EMAIL REAL en la URL - CORREGIDO CON API_URL
        const response = await fetch(`${API_URL}/api/auth/totp/qr?email=${encodeURIComponent(userEmail)}`, {
            method: "GET",
            credentials: "include"
        });

        document.getElementById("scannedBtn").addEventListener("click", () => {
            window.location.href = "../verification/verification.html";
        });

        if (!response.ok) {
            container.textContent = "No autorizado o usuario no encontrado.";
            console.error("Error QR:", response.status);
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const img = document.createElement("img");
        img.src = url;
        img.alt = "QR Code";
        img.className = "img-fluid";

        container.appendChild(img);
    } catch (error) {
        container.textContent = "Error al cargar el QR. Verifica conexión con el servidor.";
        console.error(error);
    }
});