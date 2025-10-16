import { useState, useEffect } from 'react';
import { useAuthContext } from '../contexts/AuthContext';
import { getAllUsers, createUser, updateUser, deleteUser, UsuarioResponse, UsuarioCreate, UsuarioUpdate } from '../api/users';
import { Navigate } from 'react-router-dom';

interface FormData {
  nombre: string;
  correo: string;
  contraseña: string;
  tipo: 'usuario' | 'admin';
}

export default function AdminDashboard() {
  const { user, token } = useAuthContext();
  const [usuarios, setUsuarios] = useState<UsuarioResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UsuarioResponse | null>(null);
  const [formData, setFormData] = useState<FormData>({
    nombre: '',
    correo: '',
    contraseña: '',
    tipo: 'usuario'
  });
  const [editFormData, setEditFormData] = useState<UsuarioUpdate>({});
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Verificar que el usuario es admin
  if (user?.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await getAllUsers(token);
      setUsuarios(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar usuarios');
      console.error('Error cargando usuarios:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setActionLoading(true);
    setError(null);
    try {
      const newUser: UsuarioCreate = {
        nombre: formData.nombre,
        correo: formData.correo,
        contraseña: formData.contraseña,
        tipo: formData.tipo
      };
      
      await createUser(newUser, token);
      setSuccessMessage('Usuario creado exitosamente');
      setTimeout(() => setSuccessMessage(null), 3000);
      
      // Limpiar formulario y cerrar modal
      setFormData({ nombre: '', correo: '', contraseña: '', tipo: 'usuario' });
      setShowCreateModal(false);
      
      // Recargar lista
      await loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear usuario');
      console.error('Error creando usuario:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !selectedUser) return;

    setActionLoading(true);
    setError(null);
    try {
      const updateData: UsuarioUpdate = {};
      
      if (editFormData.nombre && editFormData.nombre !== selectedUser.nombre) {
        updateData.nombre = editFormData.nombre;
      }
      if (editFormData.correo && editFormData.correo !== selectedUser.correo) {
        updateData.correo = editFormData.correo;
      }
      if (editFormData.contraseña && editFormData.contraseña.trim() !== '') {
        updateData.contraseña = editFormData.contraseña;
      }
      if (editFormData.tipo && editFormData.tipo !== selectedUser.tipo) {
        updateData.tipo = editFormData.tipo;
      }

      // Solo actualizar si hay cambios
      if (Object.keys(updateData).length === 0) {
        setError('No se detectaron cambios para actualizar');
        setActionLoading(false);
        return;
      }

      await updateUser(selectedUser.id, updateData, token);
      setSuccessMessage('Usuario actualizado exitosamente');
      setTimeout(() => setSuccessMessage(null), 3000);
      
      // Cerrar modal y limpiar
      setShowEditModal(false);
      setSelectedUser(null);
      setEditFormData({});
      
      // Recargar lista
      await loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar usuario');
      console.error('Error actualizando usuario:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string, userName: string) => {
    if (!token) return;
    
    if (!confirm(`¿Estás seguro de eliminar al usuario ${userName}?`)) {
      return;
    }

    setActionLoading(true);
    setError(null);
    try {
      await deleteUser(userId, token);
      setSuccessMessage('Usuario eliminado exitosamente');
      setTimeout(() => setSuccessMessage(null), 3000);
      
      // Recargar lista
      await loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar usuario');
      console.error('Error eliminando usuario:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const openEditModal = (usuario: UsuarioResponse) => {
    setSelectedUser(usuario);
    setEditFormData({
      nombre: usuario.nombre,
      correo: usuario.correo,
      tipo: usuario.tipo,
      contraseña: ''
    });
    setShowEditModal(true);
    setError(null);
  };

  const closeEditModal = () => {
    setShowEditModal(false);
    setSelectedUser(null);
    setEditFormData({});
    setError(null);
  };

  const closeCreateModal = () => {
    setShowCreateModal(false);
    setFormData({ nombre: '', correo: '', contraseña: '', tipo: 'usuario' });
    setError(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando usuarios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Panel de Administración</h1>
        <p className="text-gray-600">Gestiona los usuarios del sistema</p>
      </div>

      {/* Mensajes */}
      {successMessage && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
          {successMessage}
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {/* Botón crear usuario */}
      <div className="mb-6">
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          + Crear Usuario
        </button>
      </div>

      {/* Tabla de usuarios */}
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nombre
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Correo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fecha Creación
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {usuarios.map((usuario) => (
              <tr key={usuario.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {usuario.nombre}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {usuario.correo}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    usuario.tipo === 'admin' 
                      ? 'bg-purple-100 text-purple-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {usuario.tipo}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {usuario.fecha_creacion 
                    ? new Date(usuario.fecha_creacion).toLocaleDateString('es-ES') 
                    : 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => openEditModal(usuario)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                    disabled={actionLoading}
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleDeleteUser(usuario.id, usuario.nombre)}
                    className="text-red-600 hover:text-red-900"
                    disabled={actionLoading}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {usuarios.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No hay usuarios registrados
          </div>
        )}
      </div>

      {/* Modal Crear Usuario */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Crear Nuevo Usuario</h2>
            <form onSubmit={handleCreateUser}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre
                  </label>
                  <input
                    type="text"
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Correo
                  </label>
                  <input
                    type="email"
                    value={formData.correo}
                    onChange={(e) => setFormData({ ...formData, correo: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Contraseña
                  </label>
                  <input
                    type="password"
                    value={formData.contraseña}
                    onChange={(e) => setFormData({ ...formData, contraseña: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Usuario
                  </label>
                  <select
                    value={formData.tipo}
                    onChange={(e) => setFormData({ ...formData, tipo: e.target.value as 'usuario' | 'admin' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="usuario">Usuario</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={closeCreateModal}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
                  disabled={actionLoading}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                  disabled={actionLoading}
                >
                  {actionLoading ? 'Creando...' : 'Crear Usuario'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Editar Usuario */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Editar Usuario</h2>
            <form onSubmit={handleUpdateUser}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre
                  </label>
                  <input
                    type="text"
                    value={editFormData.nombre || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, nombre: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Correo
                  </label>
                  <input
                    type="email"
                    value={editFormData.correo || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, correo: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nueva Contraseña (dejar en blanco para no cambiar)
                  </label>
                  <input
                    type="password"
                    value={editFormData.contraseña || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, contraseña: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Dejar vacío para no cambiar"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Usuario
                  </label>
                  <select
                    value={editFormData.tipo || 'usuario'}
                    onChange={(e) => setEditFormData({ ...editFormData, tipo: e.target.value as 'usuario' | 'admin' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="usuario">Usuario</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={closeEditModal}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
                  disabled={actionLoading}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                  disabled={actionLoading}
                >
                  {actionLoading ? 'Guardando...' : 'Guardar Cambios'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

