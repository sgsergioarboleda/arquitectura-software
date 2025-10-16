import { useEffect, useMemo, useState } from "react";
import { listLost, claimLostItem } from "../api/lost";
import FileDropzone from "../components/FileDropzone";
import type { LostItem } from "../types";
import { useAuthContext } from "../contexts/AuthContext";

export default function LostAndFound() {
  const [items, setItems] = useState<LostItem[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<LostItem | null>(null);
  const [evidences, setEvidences] = useState<File[]>([]);
  const [notes, setNotes] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { makeRequest, isAuthenticated } = useAuthContext();
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    setLoading(true);
    setError(null);
    
    // Usar makeRequest que funciona con o sin autenticación
    makeRequest<LostItem[]>('GET', '/lost')
      .then((data) => {
        setItems(data);
      })
      .catch((error) => {
        console.error("Error al cargar objetos perdidos:", error);
        setError("Error al cargar los objetos perdidos");
        setItems([]);
      })
      .finally(() => setLoading(false));
  }, [q, makeRequest]);

  const filtered = useMemo(() => items, [items]);

  const submitClaim = async () => {
    if (!selected) return;
    
    // Verificar autenticación
    if (!isAuthenticated) {
      alert("Debes iniciar sesión para reclamar un objeto.");
      return;
    }
    
    if (evidences.length === 0) return alert("Adjunta al menos una evidencia.");
    
    setSending(true);
    setError(null);
    
    try {
      // Crear FormData para enviar archivos
      const formData = new FormData();
      formData.append('notes', notes);
      evidences.forEach((file) => {
        formData.append('evidences', file);
      });

      await makeRequest('POST', `/lost/${selected._id}/claim`, formData);
      alert("Reclamo enviado.");
      setSelected(null); 
      setEvidences([]); 
      setNotes("");
    } catch (err: any) {
      setError(err.message || "No se pudo enviar el reclamo");
    } finally { 
      setSending(false); 
    }
  };

  return (
    <div>
      <div className="mb-5 flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold">Objetos perdidos</h1>
          <p className="text-gray-600 text-sm">Busca y reclama tus pertenencias de forma segura.</p>
        </div>
        <div className="sm:ml-auto w-full sm:w-80">
          <input
            className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
            placeholder="Buscar por título o lugar…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-56 bg-white rounded-2xl border shadow-sm animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-2xl border bg-white p-10 text-center text-gray-600">
          No se encontraron objetos.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((it, index) => (
            <div key={it._id || index} className="bg-white rounded-2xl border shadow-sm overflow-hidden">
              <div className="h-40 bg-gray-100">
                {it._id ? (
                  <img
                    src={`${apiUrl}/lost/${it._id}/image`}
                    alt={it.title}
                    className="w-full h-full object-cover"
                    onError={(e) => { 
                      (e.currentTarget as HTMLImageElement).style.display = 'none';
                      (e.currentTarget.parentElement as HTMLElement).innerHTML = `
                        <div class="w-full h-full flex items-center justify-center bg-gray-200 text-gray-500 text-sm">
                          Sin imagen
                        </div>
                      `;
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-200 text-gray-500 text-sm">
                    Sin imagen
                  </div>
                )}
              </div>
              <div className="p-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-medium">{it.title}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${
                    it.status === "available" ? "bg-green-100 text-green-700" :
                    it.status === "claimed" ? "bg-yellow-100 text-yellow-700" :
                    "bg-gray-200 text-gray-700"
                  }`}>
                    {it.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{it.found_location}</p>
                {isAuthenticated ? (
                  <button
                    className="mt-3 w-full rounded-lg px-3 py-2 bg-gray-900 text-white disabled:opacity-50 hover:bg-black transition"
                    disabled={it.status !== "available" || !it._id}
                    onClick={() => setSelected(it)}
                  >
                    Reclamar
                  </button>
                ) : (
                  <button
                    className="mt-3 w-full rounded-lg px-3 py-2 bg-gray-600 text-white hover:bg-gray-700 transition"
                    onClick={() => window.location.href = '/login'}
                  >
                    Iniciar sesión para reclamar
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {selected && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl border shadow-xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Reclamar: {selected.title}</h2>
              <button onClick={() => setSelected(null)} className="text-gray-500 hover:text-gray-800">✕</button>
            </div>

            <div className="mt-4 space-y-3">
              <div>
                <label className="text-sm">Notas</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full border rounded-xl p-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900/10"
                  rows={3}
                  placeholder="Factura, número de serie, rasgos, etc."
                />
              </div>

              <div>
                <label className="block text-sm mb-1">Evidencias (imágenes o PDF)</label>
                <FileDropzone
                  onFiles={(files) => setEvidences((prev) => [...prev, ...files])}
                  accept="image/*,application/pdf"
                />
                {evidences.length > 0 && (
                  <ul className="mt-2 text-sm list-disc pl-5">
                    {evidences.map((f, i) => (
                      <li key={i}>{f.name} ({Math.round(f.size / 1024)} KB)</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="mt-5 flex gap-2 justify-end">
              <button className="border rounded-lg px-4 py-2 hover:bg-gray-50" onClick={() => setSelected(null)}>Cancelar</button>
              <button
                className="rounded-lg px-4 py-2 bg-gray-900 text-white hover:bg-black disabled:opacity-50"
                disabled={sending}
                onClick={submitClaim}
              >
                {sending ? "Enviando..." : "Enviar reclamo"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
