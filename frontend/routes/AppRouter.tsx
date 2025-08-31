import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "../components/Layout";
import Login from "../pages/Login";
import LostAndFound from "../pages/LostAndFound";
import Calendar from "../pages/Calendar";
// Cuando el backend esté, puedes envolver /objetos-perdidos con ProtectedRoute

export default function AppRouter() {
  return (
    <Layout>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/objetos-perdidos" element={<LostAndFound />} />
        <Route path="/calendario" element={<Calendar />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Layout>
  );
}
