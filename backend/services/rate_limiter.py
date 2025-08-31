from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = {}
        self.logger = logging.getLogger(__name__)

    async def is_rate_limited(self, ip: str) -> Tuple[bool, int]:
        now = datetime.now()
        if ip not in self.requests:
            self.requests[ip] = []

        # Limpiar solicitudes antiguas
        self.requests[ip] = [
            req_time for req_time in self.requests[ip]
            if now - req_time < timedelta(seconds=self.window_seconds)
        ]

        # Verificar límite
        if len(self.requests[ip]) >= self.max_requests:
            self.logger.warning(f"Rate limit exceeded for IP: {ip}")
            return True, len(self.requests[ip])

        self.requests[ip].append(now)
        return False, len(self.requests[ip])

rate_limiter = RateLimiter()