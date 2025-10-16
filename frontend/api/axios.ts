import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000", // URL fija para evitar problemas de configuración
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido, limpiar localStorage
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Redirigir al login si estamos en una página protegida
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
