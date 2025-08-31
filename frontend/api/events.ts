import type { UniEvent } from "../types";
import { api } from "./axios";

export async function getEvents() {
  const { data } = await api.get("/events");
  // Esperado: { events: UniEvent[] }
  return { events: (data.events ?? []) as UniEvent[] };
}
