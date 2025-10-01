#!/usr/bin/env python3
"""
Script para generar llaves RSA para JWT
Genera llaves en formato PKCS#8 compatibles con RS256
"""

from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_rsa_keys():
    """
    Genera un par de llaves RSA para JWT
    """
    print("🔑 Generando llaves RSA...")
    
    # Obtener el directorio base (backend)
    base_dir = Path(__file__).parent
    keys_dir = base_dir / "keys"
    
    # Crear directorio keys si no existe
    keys_dir.mkdir(exist_ok=True)
    
    # Generar llave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Obtener llave pública
    public_key = private_key.public_key()
    
    # Guardar llave privada
    private_key_path = keys_dir / "private.pem"
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Guardar llave pública
    public_key_path = keys_dir / "public.pem"
    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    print("\n✅ Llaves RSA generadas exitosamente:")
    print(f"   - {private_key_path}")
    print(f"   - {public_key_path}")
    print("\nLas llaves están en formato PKCS#8 y son compatibles con RS256")

if __name__ == "__main__":
    generate_rsa_keys()
