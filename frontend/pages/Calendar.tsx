import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { useEffect, useState } from "react";
import type { EventInput, EventContentArg } from "@fullcalendar/core";
import { useAuthContext } from "../contexts/AuthContext";
import { createEvent, updateEvent, deleteEvent } from "../api/events";

type ExtProps = { location?: string };

export default function Calendar() {
  const [events, setEvents] = useState<EventInput[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<any | null>(null);
  const { makeRequest, user, isAuthenticated } = useAuthContext();
  
  // Estado del formulario de creación
  const [formData, setFormData] = useState({
    title: "",
    start: "",
    end: "",
    location: "",
    description: "",
  });

  // Estado del formulario de edición
  const [editFormData, setEditFormData] = useState({
    title: "",
    start: "",
    end: "",
    location: "",
    description: "",
  });

  const isAdmin = isAuthenticated && user?.role?.toLowerCase() === "admin";

  const loadEvents = () => {
    setLoading(true);
    setError(null);
    
    // Usar makeRequest que funciona con o sin autenticación
    makeRequest<any[]>('GET', '/events')
      .then((events) => {
        // El backend devuelve un array directamente, mapear para FullCalendar
        const mappedEvents = events.map(e => ({ 
          id: e._id, // FullCalendar necesita 'id', el backend devuelve '_id'
          title: e.title,
          start: e.start,
          end: e.end,
          extendedProps: {
            _id: e._id, // Preservar _id en extendedProps para uso posterior
            location: e.location,
            description: e.description,
            created_at: e.created_at,
            updated_at: e.updated_at
          }
        }));
        setEvents(mappedEvents);
      })
      .catch((err) => {
        console.error("Error al cargar eventos:", err);
        setError("Error al cargar los eventos");
        setEvents([]);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEvents();
  }, [makeRequest]);

  const handleCreateEvent = async () => {
    // Validar y limpiar los campos
    const title = formData.title?.trim();
    const start = formData.start?.trim();

    console.log("Validando formulario:", { title, start, formData });

    if (!title || title === "") {
      alert("Por favor completa el título del evento");
      return;
    }

    if (!start || start === "") {
      alert("Por favor selecciona la fecha de inicio");
      return;
    }

    setCreating(true);
    setError(null);

    try {
      await makeRequest('POST', '/events', {
        title: title,
        start: new Date(start).toISOString(),
        end: formData.end && formData.end.trim() ? new Date(formData.end).toISOString() : undefined,
        location: formData.location?.trim() || undefined,
        description: formData.description?.trim() || undefined,
      });
      
      alert("Evento creado exitosamente");
      setShowCreateModal(false);
      setFormData({
        title: "",
        start: "",
        end: "",
        location: "",
        description: "",
      });
      loadEvents();
    } catch (err: any) {
      console.error("Error al crear evento:", err);
      setError(err.response?.data?.detail || "Error al crear el evento");
    } finally {
      setCreating(false);
    }
  };

  const handleEditClick = (event: any) => {
    // Normalizar el evento - puede venir de FullCalendar o de la lista
    const normalizedEvent = {
      id: event.id,
      _id: event.extendedProps?._id || event.id, // Usar _id de extendedProps primero
      title: event.title,
      start: event.start,
      end: event.end,
      location: event.extendedProps?.location,
      description: event.extendedProps?.description,
    };
    
    setSelectedEvent(normalizedEvent);
    
    // Convertir las fechas a formato datetime-local (pueden venir como Date o string)
    const startDate = normalizedEvent.start instanceof Date ? normalizedEvent.start : new Date(normalizedEvent.start);
    const endDate = normalizedEvent.end ? (normalizedEvent.end instanceof Date ? normalizedEvent.end : new Date(normalizedEvent.end)) : null;
    
    setEditFormData({
      title: normalizedEvent.title || "",
      start: formatDateTimeLocal(startDate),
      end: endDate ? formatDateTimeLocal(endDate) : "",
      location: normalizedEvent.location || "",
      description: normalizedEvent.description || "",
    });
    setShowEditModal(true);
  };

  const formatDateTimeLocal = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const handleUpdateEvent = async () => {
    if (!selectedEvent) return;

    const title = editFormData.title?.trim();
    const start = editFormData.start?.trim();

    if (!title || title === "") {
      alert("Por favor completa el título del evento");
      return;
    }

    if (!start || start === "") {
      alert("Por favor selecciona la fecha de inicio");
      return;
    }

    setEditing(true);
    setError(null);

    try {
      // Usar _id o id, lo que esté disponible
      const eventId = selectedEvent._id || selectedEvent.id;
      
      await makeRequest('PUT', `/events/${eventId}`, {
        title: title,
        start: new Date(start).toISOString(),
        end: editFormData.end && editFormData.end.trim() ? new Date(editFormData.end).toISOString() : undefined,
        location: editFormData.location?.trim() || undefined,
        description: editFormData.description?.trim() || undefined,
      });
      
      alert("Evento actualizado exitosamente");
      setShowEditModal(false);
      setSelectedEvent(null);
      setEditFormData({
        title: "",
        start: "",
        end: "",
        location: "",
        description: "",
      });
      loadEvents();
    } catch (err: any) {
      console.error("Error al actualizar evento:", err);
      setError(err.response?.data?.detail || "Error al actualizar el evento");
    } finally {
      setEditing(false);
    }
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!confirm("¿Estás seguro de que deseas eliminar este evento?")) {
      return;
    }

    setError(null);

    try {
      await makeRequest('DELETE', `/events/${eventId}`, undefined);
      alert("Evento eliminado exitosamente");
      loadEvents();
    } catch (err: any) {
      console.error("Error al eliminar evento:", err);
      setError(err.response?.data?.detail || "Error al eliminar el evento");
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Calendario</h1>
            <p className="text-sm text-gray-600">Eventos y actividades de la Universidad</p>
          </div>
        </div>
        <div className="rounded-2xl border bg-white p-8 shadow-sm flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando eventos...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Calendario</h1>
          <p className="text-sm text-gray-600">Eventos y actividades de la Universidad</p>
        </div>
        {isAdmin && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="rounded-lg px-4 py-2 bg-gray-900 text-white hover:bg-black transition"
          >
            + Crear Evento
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="rounded-2xl border bg-white p-3 shadow-sm">
        <FullCalendar
          plugins={[dayGridPlugin, interactionPlugin]}
          initialView="dayGridMonth"
          height="auto"
          events={events}
          eventContent={(arg: EventContentArg) => {
            const ext = arg.event.extendedProps as ExtProps;
            return (
              <div title={ext.location ?? ""}>
                <b>{arg.timeText}</b> <i>{arg.event.title}</i>
              </div>
            );
          }}
          eventClick={(info) => {
            if (isAdmin) {
              handleEditClick(info.event);
            }
          }}
        />
      </div>

      {/* Lista de Eventos (solo para admins) */}
      {isAdmin && events.length > 0 && (
        <div className="rounded-2xl border bg-white p-4 shadow-sm">
          <h3 className="text-lg font-semibold mb-3">Gestionar Eventos</h3>
          <div className="space-y-2">
            {events.map((event: any) => (
              <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium">{event.title}</h4>
                  <p className="text-sm text-gray-600">
                    {new Date(event.start).toLocaleDateString('es-ES', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                  {event.extendedProps?.location && (
                    <p className="text-sm text-gray-500">📍 {event.extendedProps.location}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      // Crear un evento simulado compatible con FullCalendar
                      const fcEvent = {
                        id: event.id,
                        title: event.title,
                        start: event.start,
                        end: event.end,
                        extendedProps: event.extendedProps
                      };
                      handleEditClick(fcEvent);
                    }}
                    className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    ✏️ Editar
                  </button>
                  <button
                    onClick={() => handleDeleteEvent(event.id)}
                    className="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                  >
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal de Crear Evento */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl border shadow-xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Crear Nuevo Evento</h2>
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
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  placeholder="Nombre del evento"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Fecha de Inicio *</label>
                <input
                  type="datetime-local"
                  value={formData.start}
                  onChange={(e) => setFormData({...formData, start: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Fecha de Fin</label>
                <input
                  type="datetime-local"
                  value={formData.end}
                  onChange={(e) => setFormData({...formData, end: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Ubicación</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  placeholder="Lugar del evento"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Descripción</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  rows={3}
                  placeholder="Descripción del evento"
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
                onClick={handleCreateEvent}
              >
                {creating ? "Creando..." : "Crear Evento"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Editar Evento */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl border shadow-xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Editar Evento</h2>
              <button 
                onClick={() => setShowEditModal(false)} 
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
                  value={editFormData.title}
                  onChange={(e) => setEditFormData({...editFormData, title: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  placeholder="Nombre del evento"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Fecha de Inicio *</label>
                <input
                  type="datetime-local"
                  value={editFormData.start}
                  onChange={(e) => setEditFormData({...editFormData, start: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Fecha de Fin</label>
                <input
                  type="datetime-local"
                  value={editFormData.end}
                  onChange={(e) => setEditFormData({...editFormData, end: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Ubicación</label>
                <input
                  type="text"
                  value={editFormData.location}
                  onChange={(e) => setEditFormData({...editFormData, location: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  placeholder="Lugar del evento"
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Descripción</label>
                <textarea
                  value={editFormData.description}
                  onChange={(e) => setEditFormData({...editFormData, description: e.target.value})}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  rows={3}
                  placeholder="Descripción del evento"
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
                onClick={() => setShowEditModal(false)}
              >
                Cancelar
              </button>
              <button
                className="rounded-lg px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                disabled={editing}
                onClick={handleUpdateEvent}
              >
                {editing ? "Actualizando..." : "Actualizar Evento"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
