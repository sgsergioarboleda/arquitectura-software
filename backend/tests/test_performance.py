import time
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock

class TestPerformance:
    """Suite de pruebas de rendimiento"""
    
    @pytest.fixture
    def client(self):
        """Cliente de test"""
        return TestClient(app)
    
    def test_health_endpoint_response_time(self, client):
        """Prueba que el endpoint /health responde en menos de 100ms"""
        start_time = time.perf_counter()
        response = client.get("/health")
        end_time = time.perf_counter()
        
        response_time = (end_time - start_time) * 1000  # convertir a ms
        
        assert response.status_code == 200
        assert response_time < 100, f"El endpoint tardó {response_time:.2f}ms, máximo permitido es 100ms"
        print(f"Tiempo de respuesta: {response_time:.2f}ms")
    
    def test_health_endpoint_concurrent_requests(self, client, monkeypatch):
        """Prueba que el endpoint maneja múltiples requests concurrentes"""
        import concurrent.futures
        
        # Crear un mock async para is_rate_limited
        from services.rate_limiter import rate_limiter
        async_mock = AsyncMock(return_value=(False, 0))
        monkeypatch.setattr(rate_limiter, "is_rate_limited", async_mock)
        
        def make_request(index):
            start = time.perf_counter()
            response = client.get("/health")
            end = time.perf_counter()
            return response.status_code, (end - start) * 1000
        
        # Ejecutar 10 requests concurrentes
        num_requests = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, range(num_requests)))
        
        # Verificar que todos fueron exitosos
        status_codes = [status for status, _ in results]
        response_times = [time_ms for _, time_ms in results]
        
        assert all(status == 200 for status in status_codes), "Algunos requests fallaron"
        assert all(time_ms < 200 for time_ms in response_times), "Algunos requests fueron muy lentos"
        
        avg_time = sum(response_times) / len(response_times)
        print(f"Promedio de tiempo: {avg_time:.2f}ms")
        print(f"Tiempo máximo: {max(response_times):.2f}ms")
        print(f"Tiempo mínimo: {min(response_times):.2f}ms")
    
    def test_health_endpoint_throughput(self, client, monkeypatch):
        """Prueba el throughput (requests por segundo)"""
        # Crear un mock async para is_rate_limited
        from services.rate_limiter import rate_limiter
        async_mock = AsyncMock(return_value=(False, 0))
        monkeypatch.setattr(rate_limiter, "is_rate_limited", async_mock)
        
        num_requests = 100
        start_time = time.perf_counter()
        
        for _ in range(num_requests):
            response = client.get("/health")
            assert response.status_code == 200
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        throughput = num_requests / total_time
        
        print(f"Throughput: {throughput:.2f} requests/segundo")
        print(f"Tiempo total para {num_requests} requests: {total_time:.2f}s")
        
        # Verificar que alcanza al menos 10 requests por segundo
        assert throughput >= 10, f"Throughput muy bajo: {throughput:.2f} req/s"
    
    def test_health_endpoint_memory_usage(self, client, monkeypatch):
        """Prueba el uso de memoria durante múltiples requests"""
        import tracemalloc
        
        # Crear un mock async para is_rate_limited
        from services.rate_limiter import rate_limiter
        async_mock = AsyncMock(return_value=(False, 0))
        monkeypatch.setattr(rate_limiter, "is_rate_limited", async_mock)
        
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        
        # Hacer 50 requests
        for _ in range(50):
            response = client.get("/health")
            assert response.status_code == 200
        
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        total_memory_increase = sum(stat.size_diff for stat in top_stats) / 1024 / 1024  # MB
        
        print(f"Incremento de memoria: {total_memory_increase:.2f}MB")
        
        # Verificar que no consume más de 10MB
        assert total_memory_increase < 10, f"Uso de memoria alto: {total_memory_increase:.2f}MB"
        
        tracemalloc.stop()