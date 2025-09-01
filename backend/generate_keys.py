#!/usr/bin/env python3
"""
Script para generar llaves RSA para JWT
Genera llaves en formato PKCS#8 compatibles con RS256
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import os

def generate_rsa_keys():
    """
    Genera un par de llaves RSA para JWT
    """
    print("Generando llaves RSA...")
    
    # Generar llave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Obtener llave pública
    public_key = private_key.public_key()
    
    # Crear directorio keys si no existe
    os.makedirs("keys", exist_ok=True)
    
    # Guardar llave privada en formato PKCS#8
    with open("keys/private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Guardar llave pública en formato PKCS#8
    with open("keys/public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    print("✅ Llaves RSA generadas exitosamente:")
    print("   - keys/private.pem")
    print("   - keys/public.pem")
    print("\nLas llaves están en formato PKCS#8 y son compatibles con RS256")

if __name__ == "__main__":
    generate_rsa_keys()
