from dotenv import load_dotenv
import uvicorn
import os
from pathlib import Path

def main():
    """Initialize and run the backend server"""
    try:
        # Load environment variables
        env_path = Path(__file__).parent / ".env"
        load_dotenv(dotenv_path=env_path)

        # Get configuration from environment variables
        host = os.getenv("APP_HOST", "0.0.0.0")
        port = int(os.getenv("APP_PORT", "8000"))
        reload = os.getenv("APP_DEBUG", "true").lower() == "true"

        print("[INFO] Starting backend server...")
        print(f"[INFO] Host: {host}")
        print(f"[INFO] Port: {port}")
        print(f"[INFO] Reload: {reload}")

        # Generate RSA keys if they don't exist
        keys_dir = Path(__file__).parent / "keys"
        if not (keys_dir / "private.pem").exists() or not (keys_dir / "public.pem").exists():
            print("[INFO] Generating RSA keys...")
            from generate_keys import generate_rsa_keys
            generate_rsa_keys()

        # Start the server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )

    except Exception as e:
        print(f"[ERROR] Error starting backend: {e}")
        raise e

if __name__ == "__main__":
    main()