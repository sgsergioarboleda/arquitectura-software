import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/axios';
import type { User } from '../types';

interface LoginResponse {
  token: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Verificar token al cargar
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        setAuthState({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch (error) {
        // Token o usuario inválido, limpiar localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setAuthState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    } else {
      setAuthState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, []);

  const login = useCallback(async (correo: string, contraseña: string): Promise<User> => {
    try {
      const response = await api.post<LoginResponse>('/auth/login', {
        correo,
        contraseña,
      });

      const { token } = response.data;
      
      // Decodificar el token para obtener información del usuario
      const tokenPayload = JSON.parse(atob(token.split('.')[1]));
      
      const user: User = {
        _id: tokenPayload.user_id,
        email: tokenPayload.correo,
        role: tokenPayload.tipo,
      };

      // Guardar en localStorage
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));

      // Actualizar estado
      setAuthState({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      });

      return user;
    } catch (error) {
      throw new Error('Credenciales inválidas');
    }
  }, []);

  const logout = useCallback(() => {
    // Limpiar localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Actualizar estado
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  const authenticatedRequest = useCallback(async <T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: any
  ): Promise<T> => {
    if (!authState.token) {
      throw new Error('No hay token de autenticación');
    }

    try {
      const response = await api.request<T>({
        method,
        url,
        data,
        headers: {
          Authorization: `Bearer ${authState.token}`,
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        // Token expirado o inválido
        logout();
        throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
      }
      throw error;
    }
  }, [authState.token, logout]);

  return {
    ...authState,
    login,
    logout,
    authenticatedRequest,
  };
}
