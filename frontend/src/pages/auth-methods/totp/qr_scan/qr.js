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
        // ✅ USAR EMAIL REAL en la URL
        const response = await fetch(`http://localhost:5000/api/auth/totp/qr?email=${encodeURIComponent(userEmail)}`, {
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