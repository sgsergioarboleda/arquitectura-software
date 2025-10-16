import type { UniEvent } from "../types";
import { api } from "./axios";

export async function getEvents() {
  const { data } = await api.get("/events");
  // Esperado: { events: UniEvent[] }
  return { events: (data.events ?? []) as UniEvent[] };
}

export async function createEvent(eventData: {
  title: string;
  start: string;
  end?: string;
  location?: string;
  description?: string;
}) {
  const { data } = await api.post("/events", eventData);
  return data as UniEvent;
}

export async function updateEvent(eventId: string, eventData: {
  title?: string;
  start?: string;
  end?: string;
  location?: string;
  description?: string;
}) {
  const { data } = await api.put(`/events/${eventId}`, eventData);
  return data as UniEvent;
}

export async function deleteEvent(eventId: string) {
  const { data } = await api.delete(`/events/${eventId}`);
  return data;
}
