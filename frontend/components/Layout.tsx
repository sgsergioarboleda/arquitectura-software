import { Link, useLocation } from "react-router-dom";

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const { pathname } = useLocation();
  const active = pathname === to;
  return (
    <Link
      to={to}
      className={`px-3 py-2 rounded-lg text-sm transition
        ${active ? "bg-gray-900 text-white" : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"}`}
    >
      {children}
    </Link>
  );
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/login" className="font-semibold tracking-tight">
            Universidad Sergio Arboleda 
          </Link>
          <nav className="flex items-center gap-1">
            <NavLink to="/login">Login</NavLink>
            <NavLink to="/objetos-perdidos">Objetos perdidos</NavLink>
            <NavLink to="/calendario">Calendario</NavLink>
          </nav>
        </div>
      </header>

      {/* Contenido */}
      <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>

      <footer className="py-8 text-center text-xs text-gray-500">
        Escuela de Ciencias de la Computación e IA — Proyecto académico
      </footer>
    </div>
  );
}
