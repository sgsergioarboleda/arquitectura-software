import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { useEffect, useState } from "react";
import type { EventInput, EventContentArg } from "@fullcalendar/core";
import { useAuthContext } from "../contexts/AuthContext";

type ExtProps = { location?: string };

export default function Calendar() {
  const [events, setEvents] = useState<EventInput[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { makeRequest } = useAuthContext();

  useEffect(() => {
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
  }, [makeRequest]);

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
    </div>
  );
}
