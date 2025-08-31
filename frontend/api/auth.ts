import type { User } from "../types";
import { api } from "./axios";

export async function login(email: string, password: string) {
  const { data } = await api.post("/auth/login", { email, password });
  // Esperado: { access_token, token_type: "bearer", user }
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("user", JSON.stringify(data.user));
  return data.user as User;
}
