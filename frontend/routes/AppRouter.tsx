import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "../components/Layout";
import Login from "../pages/Login";
import LostAndFound from "../pages/LostAndFound";
import Calendar from "../pages/Calendar";
import AdminDashboard from "../pages/AdminDashboard";
import AdminRoute from "../components/AdminRoute";

function HomePage() {
  // Redirigir directamente a objetos perdidos
  return <Navigate to="/objetos-perdidos" replace />;
}

export default function AppRouter() {
  return (
    <Layout>
      <Routes>
        <Route path="/login" element={<Login />} />
        {/* Rutas públicas - accesibles sin autenticación */}
        <Route path="/objetos-perdidos" element={<LostAndFound />} />
        <Route path="/calendario" element={<Calendar />} />
        {/* Ruta protegida solo para administradores */}
        <Route 
          path="/admin" 
          element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          } 
        />
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
