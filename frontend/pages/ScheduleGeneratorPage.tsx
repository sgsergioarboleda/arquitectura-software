// src/pages/ScheduleGeneratorPage.tsx
import { useState } from "react";
import type { GeneratedSlot } from "../types";

export default function ScheduleGeneratorPage() {
  const [file, setFile] = useState<File | null>(null);
  const [scenario, setScenario] = useState<1 | 2>(1);
  const [query, setQuery] = useState("");
  const [scenario1, setScenario1] = useState<GeneratedSlot[]>([]);
  const [scenario2, setScenario2] = useState<GeneratedSlot[]>([]);
  const [loading, setLoading] = useState(false);

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

    // TODO: aquí luego llamarán a la API real.
    // Por ahora puedes simular datos de prueba:
    setTimeout(() => {
      const demo: GeneratedSlot[] = [
        {
          id: "1",
          subject: "Programación II",
          teacher: "Juan Pérez",
          day: "Lunes",
          start: "08:00",
          end: "10:00",
          room: "302",
        },
        {
          id: "2",
          subject: "Cálculo I",
          teacher: "Ana Gómez",
          day: "Martes",
          start: "10:00",
          end: "12:00",
          room: "204",
        },
      ];
      setScenario1(demo);
      setScenario2(
        demo.map((s) => ({ ...s, id: s.id + "_alt", day: "Miércoles" }))
      );
      setLoading(false);
    }, 1000);
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
    </div>
  );
}
