#!/usr/bin/env python3
"""
Script de instalación rápida para el Sistema de Gestión Universitaria
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Ejecutar comando y manejar errores"""
    print(f"🔧 Ejecutando: {command}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Detalles: {e.stderr}")
        return False

def check_requirements():
    """Verificar requisitos del sistema"""
    print("🔍 Verificando requisitos del sistema...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Verificar Node.js
    if not run_command("node --version", check=False):
        print("❌ Error: Node.js no está instalado")
        print("💡 Instala Node.js desde: https://nodejs.org/")
        return False
    
    # Verificar npm
    if not run_command("npm --version", check=False):
        print("❌ Error: npm no está instalado")
        return False
    
    print("✅ Node.js y npm detectados")
    return True

def setup_backend():
    """Configurar backend"""
    print("\n🔧 Configurando Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Error: Directorio backend no encontrado")
        return False
    
    # Instalar dependencias Python
    print("📦 Instalando dependencias Python...")
    if not run_command("pip install -r requirements.txt", cwd="backend"):
        print("❌ Error al instalar dependencias Python")
        return False
    
    # Verificar archivo .env
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  Archivo .env no encontrado")
        print("💡 Copia env.example a .env y configura tus credenciales de MongoDB")
        return False
    
    print("✅ Backend configurado")
    return True

def setup_frontend():
    """Configurar frontend"""
    print("\n⚛️  Configurando Frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Error: Directorio frontend no encontrado")
        return False
    
    # Instalar dependencias Node.js
    print("📦 Instalando dependencias Node.js...")
    if not run_command("npm install", cwd="frontend"):
        print("❌ Error al instalar dependencias Node.js")
        return False
    
    # Crear archivo .env.local si no existe
    env_local = frontend_dir / ".env.local"
    if not env_local.exists():
        print("📝 Creando archivo .env.local...")
        with open(env_local, "w") as f:
            f.write("VITE_API_URL=http://localhost:8000\n")
    
    print("✅ Frontend configurado")
    return True

def main():
    """Función principal"""
    print("🎓 Sistema de Gestión Universitaria - Instalación")
    print("=" * 60)
    
    # Verificar requisitos
    if not check_requirements():
        sys.exit(1)
    
    # Configurar backend
    if not setup_backend():
        print("\n❌ Error en la configuración del backend")
        sys.exit(1)
    
    # Configurar frontend
    if not setup_frontend():
        print("\n❌ Error en la configuración del frontend")
        sys.exit(1)
    
    print("\n🎉 ¡Instalación completada!")
    print("\n📋 Próximos pasos:")
    print("1. Configura tu base de datos MongoDB en backend/.env")
    print("2. Ejecuta: python backend/test_connection.py")
    print("3. Ejecuta: python backend/scripts/populate_db.py")
    print("4. Ejecuta: python start_dev.py")
    print("\n📚 Documentación:")
    print("- Backend: http://localhost:8000/docs")
    print("- Frontend: http://localhost:5173")

if __name__ == "__main__":
    main()
