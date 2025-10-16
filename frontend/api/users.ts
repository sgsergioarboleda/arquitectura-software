import { api } from './axios';

export interface UsuarioResponse {
  id: string;
  nombre: string;
  correo: string;
  tipo: 'usuario' | 'admin';
  fecha_creacion?: string;
}

export interface UsuarioCreate {
  nombre: string;
  correo: string;
  contraseña: string;
  tipo: 'usuario' | 'admin';
}

export interface UsuarioUpdate {
  nombre?: string;
  correo?: string;
  contraseña?: string;
  tipo?: 'usuario' | 'admin';
}

/**
 * Obtener todos los usuarios (solo admin)
 */
export async function getAllUsers(token: string): Promise<UsuarioResponse[]> {
  const response = await api.get<UsuarioResponse[]>('/admin/users/', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}

/**
 * Obtener un usuario por ID (solo admin)
 */
export async function getUserById(userId: string, token: string): Promise<UsuarioResponse> {
  const response = await api.get<UsuarioResponse>(`/admin/users/${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}

/**
 * Crear un nuevo usuario (solo admin)
 */
export async function createUser(usuario: UsuarioCreate, token: string): Promise<UsuarioResponse> {
  const response = await api.post<UsuarioResponse>('/admin/users/', usuario, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}

/**
 * Actualizar un usuario (solo admin)
 */
export async function updateUser(
  userId: string,
  usuario: UsuarioUpdate,
  token: string
): Promise<UsuarioResponse> {
  const response = await api.put<UsuarioResponse>(`/admin/users/${userId}`, usuario, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}

/**
 * Eliminar un usuario (solo admin)
 */
export async function deleteUser(userId: string, token: string): Promise<void> {
  await api.delete(`/admin/users/${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Buscar usuario por email (solo admin)
 */
export async function searchUserByEmail(email: string, token: string): Promise<UsuarioResponse> {
  const response = await api.get<UsuarioResponse>(`/admin/users/search/email/${email}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
}

