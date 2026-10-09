"""
Rate Limiting Middleware
Implements rate limiting using Redis for API protection
"""

from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import hashlib

from app.core.redis import get_redis_client


class RateLimiter:
    """
    Rate limiter middleware using Redis.
    
    Implements sliding window rate limiting.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limits
        redis_client = await get_redis_client()
        
        # Check minute limit
        minute_key = f"rate_limit:minute:{client_id}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        minute_count = await redis_client.incr(minute_key)
        
        if minute_count == 1:
            await redis_client.expire(minute_key, 60)
        
        if minute_count > self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "details": {
                            "limit": self.requests_per_minute,
                            "window": "1 minute"
                        }
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": str(max(0, self.requests_per_minute - minute_count)),
                    "X-RateLimit-Reset": str(int((datetime.utcnow() + timedelta(minutes=1)).timestamp()))
                }
            )
        
        # Check hourly limit
        hour_key = f"rate_limit:hour:{client_id}:{datetime.utcnow().strftime('%Y%m%d%H')}"
        hour_count = await redis_client.incr(hour_key)
        
        if hour_count == 1:
            await redis_client.expire(hour_key, 3600)
        
        if hour_count > self.requests_per_hour:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Hourly rate limit exceeded. Please try again later.",
                        "details": {
                            "limit": self.requests_per_hour,
                            "window": "1 hour"
                        }
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_hour),
                    "X-RateLimit-Remaining": str(max(0, self.requests_per_hour - hour_count))
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - minute_count))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user from token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Use token hash as identifier
            return hashlib.sha256(token.encode()).hexdigest()[:16]
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return hashlib.sha256(client_ip.encode()).hexdigest()[:16]
