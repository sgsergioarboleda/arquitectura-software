// src/types/index.ts
export type User = {
  _id: string;
  email: string;
  role: "student" | "admin";
};

export type LostItem = {
  _id: string;
  title: string;
  found_location: string;
  status: "available" | "claimed" | "returned";
  description?: string;
  contact_info?: string;
  created_at: string;
  updated_at?: string;
};

export type UniEvent = {
  _id?: string;
  title: string;
  start: string;  // ISO string
  end?: string;   // ISO string
  location?: string;
  description?: string;
};
