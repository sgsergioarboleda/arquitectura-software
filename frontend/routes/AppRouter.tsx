import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "../components/Layout";
import Login from "../pages/Login";
import LostAndFound from "../pages/LostAndFound";
import Calendar from "../pages/Calendar";
import AdminDashboard from "../pages/AdminDashboard";
import ProtectedRoute from "../components/ProtectedRoute";
import { useAuthContext } from "../contexts/AuthContext";

function HomePage() {
  const { isAuthenticated } = useAuthContext();
  
  if (isAuthenticated) {
    return <Navigate to="/objetos-perdidos" replace />;
  }
  
  return <Navigate to="/login" replace />;
}

export default function AppRouter() {
  return (
    <Layout>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route 
          path="/objetos-perdidos" 
          element={
            <ProtectedRoute>
              <LostAndFound />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/calendario" 
          element={
            <ProtectedRoute>
              <Calendar />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin" 
          element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          } 
        />
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
