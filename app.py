from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Crear instancia de FastAPI
app = FastAPI(
    title="API de Arquitectura de Software",
    description="API base para el proyecto de Arquitectura de Software",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {"message": "Bienvenido a la API de Arquitectura de Software"}

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud de la API"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "La API está funcionando correctamente",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
