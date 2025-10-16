import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000", // URL fija para evitar problemas de configuración
});

// Rutas públicas que no requieren autenticación
const PUBLIC_ROUTES = ['/lost', '/events', '/health', '/auth/login'];

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  const isPublicRoute = PUBLIC_ROUTES.some(route => config.url?.startsWith(route));
  
  // Solo agregar token si existe Y no es una ruta pública
  // O agregar token si existe pero permitir que el backend lo ignore en rutas públicas
  if (token && !isPublicRoute) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
});

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const isPublicRoute = PUBLIC_ROUTES.some(route => error.config?.url?.startsWith(route));
    
    // Solo redirigir al login si es 401 en rutas protegidas
    if (status === 401 && !isPublicRoute) {
      // Token expirado o inválido, limpiar localStorage
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Redirigir al login si estamos en una página protegida
      if (window.location.pathname !== "/login" && 
          window.location.pathname !== "/objetos-perdidos" &&
          window.location.pathname !== "/calendario") {
        window.location.href = "/login";
      }
    }
    
    // Si es 403 en ruta pública, limpiar token corrupto
    if (status === 403 && isPublicRoute) {
      console.warn("Token inválido detectado en ruta pública, limpiando...");
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Reintentar la petición sin token
      return api.request(error.config);
    }
    
    return Promise.reject(error);
  }
);
