import type { LostItem } from "../types";
import { api } from "./axios";

export async function listLost(q?: string) {
  const { data } = await api.get("/lost", { params: { q } });
  if (Array.isArray(data) && data.length > 0) {
    console.log("Campos del primer elemento:", Object.keys(data[0]));
  }
  
  return (data ?? []) as LostItem[];
}

export async function claimLostItem(id: string, files: File[], notes: string) {
  const form = new FormData();
  files.forEach((f) => form.append("evidences", f));
  form.append("notes", notes);
  const { data } = await api.post(`/lost/${id}/claim`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function createLostItem(itemData: {
  title: string;
  found_location: string;
  description?: string;
  contact_info?: string;
}) {
  const { data } = await api.post("/lost/create", itemData);
  return data as LostItem;
}
