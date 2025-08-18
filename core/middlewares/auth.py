from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import correct_token


class AuthMiddleWare(BaseHTTPMiddleware):
    """
    Middleware that enforces access with a valid API token from config.py.

    Accepted headers:
      - Authorization: Bearer <TOKEN>
      - X-API-Token: <TOKEN>
    """

    PUBLIC_PATHS = {"/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        # Allow docs and OpenAPI without token
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        expected_token = correct_token
        if not expected_token:
            # Server misconfiguration: required token is not set
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API token is not configured on the server",
            )

        # Try Authorization: Bearer <token>
        auth_header = request.headers.get("Authorization")
        provided_token = None
        if auth_header and auth_header.startswith("Bearer "):
            provided_token = auth_header.split(" ", 1)[1].strip()

        # Fallback to X-API-Token header
        if not provided_token:
            provided_token = request.headers.get("X-API-Token")

        if not provided_token or provided_token != expected_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)


