import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { useEffect, useState } from "react";
import { getEvents } from "../api/events";
import type { EventInput, EventContentArg } from "@fullcalendar/core";

type ExtProps = { location?: string };

export default function Calendar() {
  const [events, setEvents] = useState<EventInput[]>([]);

  useEffect(() => {
    getEvents().then(({ events }) => setEvents(events.map(e => ({ ...e })))).catch(() => setEvents([]));
  }, []);

  return (
    <div className="space-y-3">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Calendario</h1>
          <p className="text-sm text-gray-600">Eventos y actividades de la Universidad</p>
        </div>
      </div>

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
