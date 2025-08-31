import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { login } from "../api/auth";
import { useNavigate } from "react-router-dom";

const schema = z.object({
  email: z.string().email("Correo inválido"),
  password: z.string().min(6, "Mínimo 6 caracteres"),
});
type FormData = z.infer<typeof schema>;

export default function Login() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<FormData>({ resolver: zodResolver(schema) });
  const navigate = useNavigate();

  const onSubmit = async (data: FormData) => {
    try {
      await login(data.email, data.password);
      navigate("/objetos-perdidos");
    } catch {
      alert("Credenciales inválidas o servidor no disponible");
    }
  };

  return (
    <div className="grid lg:grid-cols-2 gap-8 items-center">
      <div className="hidden lg:block">
        <div className="rounded-3xl border bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-semibold mb-3">Bienvenido 👋</h2>
          <p className="text-gray-600">
            Portal académico para gestionar objetos perdidos, eventos y más.
          </p>
          <div className="mt-6 aspect-[16/10] rounded-2xl bg-gradient-to-br from-indigo-200 via-sky-200 to-emerald-200" />
        </div>
      </div>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="bg-white p-6 rounded-2xl border shadow-sm w-full max-w-md mx-auto space-y-4"
      >
        <h1 className="text-2xl font-semibold">Iniciar sesión</h1>
        <p className="text-sm text-gray-600">Usa tu correo institucional.</p>

        <div>
          <label className="block text-sm mb-1">Correo</label>
          <input
            className="w-full border rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-gray-900/20"
            {...register("email")}
            placeholder="tu@sergio.edu"
          />
          {errors.email && <p className="text-red-600 text-sm">{errors.email.message}</p>}
        </div>

        <div>
          <label className="block text-sm mb-1">Contraseña</label>
          <input
            type="password"
            className="w-full border rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-gray-900/20"
            {...register("password")}
          />
          {errors.password && <p className="text-red-600 text-sm">{errors.password.message}</p>}
        </div>

        <button
          disabled={isSubmitting}
          className="w-full rounded-lg p-3 bg-gray-900 text-white hover:bg-black transition disabled:opacity-60"
        >
          {isSubmitting ? "Ingresando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
