import type { User } from "../types";
import { api } from "./axios";

interface LoginResponse {
  token: string;
}

export async function login(correo: string, contraseña: string): Promise<User> {
  const { data } = await api.post<LoginResponse>("/auth/login", { 
    correo, 
    contraseña 
  });
  
  // Decodificar el token para obtener información del usuario
  const tokenPayload = JSON.parse(atob(data.token.split('.')[1]));
  
  const user: User = {
    _id: tokenPayload.user_id,
    email: tokenPayload.correo,
    role: tokenPayload.tipo,
  };

  // Guardar token y usuario
  localStorage.setItem("token", data.token);
  localStorage.setItem("user", JSON.stringify(user));
  
  return user;
}

export function logout(): void {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

export function getCurrentUser(): User | null {
  const userStr = localStorage.getItem("user");
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
}

export function isAuthenticated(): boolean {
  return localStorage.getItem("token") !== null;
}
