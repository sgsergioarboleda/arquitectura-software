import { useEffect, useMemo, useState } from "react";
import type { LostItem } from "../types";
import { useAuthContext } from "../contexts/AuthContext";

export default function LostAndFound() {
  const [items, setItems] = useState<LostItem[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<LostItem | null>(null);
  const [showContactModal, setShowContactModal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const { makeRequest, isAuthenticated, user } = useAuthContext();
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  
  // Estado del formulario de creación
  const [createFormData, setCreateFormData] = useState({
    title: "",
    found_location: "",
    description: "",
    contact_info: "",
  });

  const isAdmin = isAuthenticated && user?.role?.toLowerCase() === "admin";

  const loadItems = () => {
    setLoading(true);
    setError(null);
    
    // Usar makeRequest que funciona con o sin autenticación
    makeRequest<LostItem[]>('GET', '/lost')
      .then((data) => {
        setItems(data);
      })
      .catch((error) => {
        console.error("Error al cargar objetos perdidos:", error);
        setError("Error al cargar los objetos perdidos");
        setItems([]);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadItems();
  }, [q, makeRequest]);

  const filtered = useMemo(() => items, [items]);

  const handleClaimClick = (item: LostItem) => {
    // Verificar autenticación
    if (!isAuthenticated) {
      alert("Debes iniciar sesión para ver los detalles de contacto.");
      return;
    }
    
    setSelected(item);
    setShowContactModal(true);
  };

  const handleCreateItem = async () => {
    // Validar y limpiar los campos
    const title = createFormData.title?.trim();
    const foundLocation = createFormData.found_location?.trim();

    console.log("Validando formulario:", { title, foundLocation, createFormData });

    if (!title || title === "") {
      alert("Por favor completa el título del objeto");
      return;
    }

    if (!foundLocation || foundLocation === "") {
      alert("Por favor completa el lugar donde se encontró");
      return;
    }

    setCreating(true);
    setError(null);

    try {
      await makeRequest('POST', '/lost/create', {
        title: title,
        found_location: foundLocation,
        description: createFormData.description?.trim() || undefined,
        contact_info: createFormData.contact_info?.trim() || undefined,
      });
      
      alert("Objeto perdido creado exitosamente");
      setShowCreateModal(false);
      setCreateFormData({
        title: "",
        found_location: "",
        description: "",
        contact_info: "",
      });
      loadItems();
    } catch (err: any) {
      console.error("Error al crear objeto perdido:", err);
      setError(err.response?.data?.detail || "Error al crear el objeto perdido");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div>
      <div className="mb-5 flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold">Objetos perdidos</h1>
          <p className="text-gray-600 text-sm">Busca y reclama tus pertenencias de forma segura.</p>
        </div>
        <div className="sm:ml-auto flex gap-3 w-full sm:w-auto">
          <div className="flex-1 sm:flex-initial sm:w-80">
            <input
              className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
              placeholder="Buscar por título o lugar…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
          {isAdmin && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="rounded-lg px-4 py-2 bg-gray-900 text-white hover:bg-black transition whitespace-nowrap"
            >
              + Añadir Objeto
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-56 bg-white rounded-2xl border shadow-sm animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-2xl border bg-white p-10 text-center text-gray-600">
          No se encontraron objetos.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((it, index) => (
            <div key={it._id || index} className="bg-white rounded-2xl border shadow-sm overflow-hidden">
                <div className="h-40 bg-gray-100">
                  {it._id ? (
                    <img
                      src={`${apiUrl}/lost/${it._id}/image`}
                      alt={it.title}
                      className="w-full h-full object-cover"
                      onError={(e) => { 
                        (e.currentTarget as HTMLImageElement).style.display = 'none';
                        (e.currentTarget.parentElement as HTMLElement).innerHTML = `
                          <div class="w-full h-full flex items-center justify-center bg-gray-200 text-gray-500 text-sm">
                            Sin imagen
                          </div>
                        `;
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-200 text-gray-500 text-sm">
                      Sin imagen
                    </div>
                  )}
                </div>
                <div className="p-3">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-medium">{it.title}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${
                      it.status === "available" ? "bg-green-100 text-green-700" :
                      it.status === "claimed" ? "bg-yellow-100 text-yellow-700" :
                      "bg-gray-200 text-gray-700"
                    }`}>
                      {it.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{it.found_location}</p>
                  {isAuthenticated ? (
                    <button
                      className="mt-3 w-full rounded-lg px-3 py-2 bg-gray-900 text-white disabled:opacity-50 hover:bg-black transition"
                      disabled={it.status !== "available" || !it._id}
                      onClick={() => handleClaimClick(it)}
                    >
                      Reclamar
                    </button>
                  ) : (
                    <button
                      className="mt-3 w-full rounded-lg px-3 py-2 bg-gray-600 text-white hover:bg-gray-700 transition"
                      onClick={() => window.location.href = '/login'}
                    >
                      Iniciar sesión para reclamar
                    </button>
                  )}
                </div>
              </div>
            ))}
        </div>
      )}

      {/* Modal de Información de Contacto */}
      {showContactModal && selected && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl border shadow-xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Información de Contacto</h2>
              <button 
                onClick={() => {
                  setShowContactModal(false);
                  setSelected(null);
                }} 
                className="text-gray-500 hover:text-gray-800"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              {/* Detalles del objeto */}
              <div className="bg-gray-50 rounded-xl p-4">
                <h3 className="font-semibold text-gray-900 mb-2">{selected.title}</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Lugar encontrado:</span>
                    <span className="ml-2 font-medium">{selected.found_location}</span>
                  </div>
                  {selected.description && (
                    <div>
                      <span className="text-gray-600">Descripción:</span>
                      <p className="mt-1 text-gray-800">{selected.description}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Información de contacto */}
              {selected.contact_info ? (
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">📞 Contacto</h4>
                  <p className="text-blue-800">{selected.contact_info}</p>
                </div>
              ) : (
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                  <p className="text-gray-600 text-sm">No hay información de contacto específica disponible.</p>
                </div>
              )}

              {/* Mensaje de Dirección Estudiantil */}
              <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">🏢</span>
                  <div>
                    <h4 className="font-semibold text-green-900 mb-1">Dirección Estudiantil</h4>
                    <p className="text-green-800 text-sm">
                      En caso de necesitarlo, acérquese a Dirección Estudiantil para más información o para completar el proceso de reclamo.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-5 flex justify-end">
              <button 
                className="rounded-lg px-4 py-2 bg-gray-900 text-white hover:bg-black transition" 
                onClick={() => {
                  setShowContactModal(false);
                  setSelected(null);
                }}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Crear Objeto Perdido */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl border shadow-xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Añadir Objeto Perdido</h2>
              <button 
                onClick={() => setShowCreateModal(false)} 
                className="text-gray-500 hover:text-gray-800"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-sm mb-1">Título *</label>
                <input
                  type="text"
                  value={createFormData.title}
                  onChange={(e) => setCreateFormData({...createFormData, title: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  placeholder="Nombre del objeto"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Lugar donde se encontró *</label>
                <input
                  type="text"
                  value={createFormData.found_location}
                  onChange={(e) => setCreateFormData({...createFormData, found_location: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  placeholder="Ej: Biblioteca, Cafetería, Salón 301"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Descripción</label>
                <textarea
                  value={createFormData.description}
                  onChange={(e) => setCreateFormData({...createFormData, description: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  rows={3}
                  placeholder="Descripción detallada del objeto"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Información de contacto</label>
                <input
                  type="text"
                  value={createFormData.contact_info}
                  onChange={(e) => setCreateFormData({...createFormData, contact_info: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  placeholder="Email o teléfono de contacto"
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}
            </div>

            <div className="mt-5 flex gap-2 justify-end">
              <button 
                className="border rounded-lg px-4 py-2 hover:bg-gray-50" 
                onClick={() => setShowCreateModal(false)}
              >
                Cancelar
              </button>
              <button
                className="rounded-lg px-4 py-2 bg-gray-900 text-white hover:bg-black disabled:opacity-50"
                disabled={creating}
                onClick={handleCreateItem}
              >
                {creating ? "Creando..." : "Crear Objeto"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
