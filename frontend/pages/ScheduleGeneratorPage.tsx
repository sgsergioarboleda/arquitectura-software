// src/pages/ScheduleGeneratorPage.tsx
import { useState } from "react";
import type { GeneratedSlot } from "../types";
import { generateSchedule, ScheduledSession } from "../api/schedule";

export default function ScheduleGeneratorPage() {
  const [file, setFile] = useState<File | null>(null);
  const [scenario, setScenario] = useState<1 | 2>(1);
  const [query, setQuery] = useState("");
  const [scenario1, setScenario1] = useState<GeneratedSlot[]>([]);
  const [scenario2, setScenario2] = useState<GeneratedSlot[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [justification, setJustification] = useState<string | null>(null);
  const [stats, setStats] = useState<{ scheduled: number; unscheduled: number } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    setFile(f);
  };

  const handleGenerate = async () => {
    if (!file) {
      alert("Por favor selecciona un archivo Excel primero.");
      return;
    }
    
    setLoading(true);
    setError(null);
    setJustification(null);

    try {
      const result = await generateSchedule(file);
      
      // Convert scheduled sessions to GeneratedSlot format
      const convertedSlots: GeneratedSlot[] = result.scheduled.map((session: ScheduledSession) => {
        const [start, end] = session.Horario.split('-');
        return {
          id: `${session.idx}`,
          subject: session.clase,
          teacher: session.Profesor,
          day: getDayName(session.dia),
          start: start.trim(),
          end: end.trim(),
          room: session.Salon,
        };
      });
      
      setScenario1(convertedSlots);
      // For now, we'll use the same result for both scenarios
      // In future, you could call the API twice or implement different strategies
      setScenario2(convertedSlots);
      
      setStats({
        scheduled: result.total_scheduled,
        unscheduled: result.total_unscheduled
      });
      
      if (result.justification) {
        setJustification(result.justification);
      }
      
      if (result.total_unscheduled > 0) {
        alert(`Horario generado con ${result.total_scheduled} sesiones programadas y ${result.total_unscheduled} sesiones no programadas. Revisa las recomendaciones al final de la página.`);
      }
      
    } catch (err: any) {
      console.error("Error generating schedule:", err);
      const errorMessage = err.response?.data?.detail || err.message || "Error desconocido al generar el horario";
      setError(errorMessage);
      alert(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };
  
  // Helper function to convert day codes to full names
  const getDayName = (dayCode: string): string => {
    const dayMap: Record<string, string> = {
      'L': 'Lunes',
      'M': 'Martes',
      'X': 'Miércoles',
      'J': 'Jueves',
      'V': 'Viernes'
    };
    return dayMap[dayCode] || dayCode;
  };

  const currentData = (scenario === 1 ? scenario1 : scenario2).filter((slot) =>
    slot.subject.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-semibold mb-2">Generación de horarios</h1>
      <p className="text-sm text-gray-600 mb-4">
        Sube el archivo Excel con la plantilla de horarios de profesores. El
        sistema generará dos posibles propuestas de horario por semestre. Puedes
        buscar por materia y alternar entre las propuestas.
      </p>

      {/* Panel de carga y acciones */}
      <div className="border rounded-lg p-4 space-y-4 bg-white shadow-sm">
        <div>
          <label className="block text-sm font-medium mb-1">
            Archivo Excel de entrada
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileChange}
            className="block w-full text-sm"
          />
          <p className="text-xs text-gray-500 mt-1">
            Usa siempre la misma plantilla acordada con el coordinador.
          </p>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading || !file}
          className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm font-medium disabled:opacity-50"
        >
          {loading ? "Generando horarios..." : "Subir y generar horarios"}
        </button>
        
        {error && (
          <div className="p-3 rounded-md bg-red-50 border border-red-200 text-red-700 text-sm">
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {stats && (
          <div className="p-3 rounded-md bg-blue-50 border border-blue-200 text-sm">
            <strong>Resultado:</strong> {stats.scheduled} sesiones programadas, {stats.unscheduled} no programadas
          </div>
        )}
      </div>

      {/* Panel de selección y búsqueda */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Propuesta:</span>
          <button
            onClick={() => setScenario(1)}
            className={`px-3 py-1 text-sm rounded-md border ${
              scenario === 1 ? "bg-blue-600 text-white" : "bg-white"
            }`}
          >
            Propuesta 1
          </button>
          <button
            onClick={() => setScenario(2)}
            className={`px-3 py-1 text-sm rounded-md border ${
              scenario === 2 ? "bg-blue-600 text-white" : "bg-white"
            }`}
          >
            Propuesta 2
          </button>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm">Buscar por materia:</label>
          <input
            type="text"
            placeholder="Ej: Programación II"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="border rounded-md px-2 py-1 text-sm"
          />
        </div>
      </div>

      {/* Tabla de resultados */}
      <div className="border rounded-lg bg-white shadow-sm overflow-x-auto">
        {currentData.length === 0 ? (
          <p className="p-4 text-sm text-gray-500">
            {loading
              ? "Generando horarios..."
              : "Aún no hay horarios generados o no hay coincidencias con la búsqueda."}
          </p>
        ) : (
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-3 py-2 text-left">Materia</th>
                <th className="px-3 py-2 text-left">Profesor</th>
                <th className="px-3 py-2 text-left">Día</th>
                <th className="px-3 py-2 text-left">Hora</th>
                <th className="px-3 py-2 text-left">Salón</th>
              </tr>
            </thead>
            <tbody>
              {currentData.map((slot) => (
                <tr key={slot.id} className="border-t">
                  <td className="px-3 py-2">{slot.subject}</td>
                  <td className="px-3 py-2">{slot.teacher}</td>
                  <td className="px-3 py-2">{slot.day}</td>
                  <td className="px-3 py-2">
                    {slot.start} - {slot.end}
                  </td>
                  <td className="px-3 py-2">{slot.room}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {/* Justification section */}
      {justification && (
        <div className="border rounded-lg bg-yellow-50 shadow-sm p-4">
          <h2 className="text-lg font-semibold mb-2">Recomendaciones y análisis</h2>
          <div className="text-sm whitespace-pre-wrap">{justification}</div>
        </div>
      )}
    </div>
  );
}
