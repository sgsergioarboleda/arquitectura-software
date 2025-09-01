#!/usr/bin/env python3
"""
Script para ejecutar el sistema completo en modo desarrollo
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Ejecutar comando y retornar el proceso"""
    print(f"🚀 Ejecutando: {command}")
    return subprocess.Popen(
        command,
        cwd=cwd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

def main():
    """Función principal"""
    print("🎓 Sistema de Gestión Universitaria")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Error: Debes ejecutar este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    processes = []
    
    try:
        # Ejecutar backend
        print("\n🔧 Iniciando Backend...")
        backend_process = run_command("python run.py", cwd="backend")
        processes.append(("Backend", backend_process))
        
        # Esperar un poco para que el backend inicie
        time.sleep(3)
        
        # Ejecutar frontend
        print("\n⚛️  Iniciando Frontend...")
        frontend_process = run_command("npm run dev", cwd="frontend")
        processes.append(("Frontend", frontend_process))
        
        print("\n✅ Sistema iniciado correctamente!")
        print("\n📱 URLs disponibles:")
        print("   - Frontend: http://localhost:5173")
        print("   - Backend API: http://localhost:8000")
        print("   - API Docs: http://localhost:8000/docs")
        print("\n⏹️  Presiona Ctrl+C para detener todos los servicios")
        
        # Mantener el script ejecutándose
        while True:
            time.sleep(1)
            
            # Verificar si algún proceso se cerró
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n❌ {name} se cerró inesperadamente")
                    return
            
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo servicios...")
        
        # Detener todos los procesos
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} detenido")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 {name} forzado a cerrar")
            except Exception as e:
                print(f"❌ Error al detener {name}: {e}")
        
        print("\n👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()
