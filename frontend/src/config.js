// Configuración automática para desarrollo/producción
const API_URL = (() => {
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5000';  // Desarrollo
  } else {
    return 'https://auth-backend.onrender.com';  // Producción - CAMBIARÁS ESTO
  }
})();