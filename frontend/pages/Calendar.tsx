import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { useEffect, useState } from "react";
import type { EventInput, EventContentArg } from "@fullcalendar/core";
import { useAuthContext } from "../contexts/AuthContext";
import { createEvent } from "../api/events";

type ExtProps = { location?: string };

export default function Calendar() {
  const [events, setEvents] = useState<EventInput[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const { makeRequest, user, isAuthenticated } = useAuthContext();
  
  // Estado del formulario
  const [formData, setFormData] = useState({
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
        // El backend devuelve un array directamente, no un objeto { events: [] }
        setEvents(events.map(e => ({ ...e })));
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
        />
      </div>

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
    </div>
  );
}
