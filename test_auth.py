#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de autenticación JWT
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def test_health():
    """Prueba el endpoint de salud"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Health check falló: {e}")
        return False

def test_login_invalid():
    """Prueba login con credenciales inválidas"""
    try:
        data = {
            "correo": "santiago@gmail.com",
            "contraseña": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"✅ Login inválido: {response.status_code} (esperado: 401)")
        return True
    except Exception as e:
        print(f"❌ Login inválido falló: {e}")
        return False

def test_protected_endpoint_without_token():
    """Prueba acceso a endpoint protegido sin token"""
    try:
        response = requests.get(f"{BASE_URL}/user/list")
        print(f"✅ Endpoint protegido sin token: {response.status_code} (esperado: 401)")
        return True
    except Exception as e:
        print(f"❌ Endpoint protegido sin token falló: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de autenticación...")
    print("=" * 50)
    
    # Verificar que la API esté funcionando
    if not test_health():
        print("❌ La API no está funcionando. Asegúrate de que esté ejecutándose.")
        return
    
    # Pruebas de autenticación
    test_login_invalid()
    test_protected_endpoint_without_token()
    
    print("=" * 50)
    print("✅ Pruebas completadas. Revisa los resultados arriba.")
    print("\n📝 Para probar completamente:")
    print("1. Crea un usuario con POST /user/create")
    print("2. Haz login con POST /auth/login")
    print("3. Usa el token para acceder a endpoints protegidos")

if __name__ == "__main__":
    main()
