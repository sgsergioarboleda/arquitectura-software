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
};

export type UniEvent = {
  _id?: string;
  title: string;
  start: string;  // ISO string
  end?: string;   // ISO string
  location?: string;
  description?: string;
};
