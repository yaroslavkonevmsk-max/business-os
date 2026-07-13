import aiohttp
from typing import Any

from app.config import settings


class ApiAuthError(Exception):
    """Raised when backend returns 401 or auth fails."""
    pass


class ApiClientError(Exception):
    """Raised for general API errors (4xx, 5xx)."""
    def __init__(self, status: int, detail: str = ""):
        self.status = status
        self.detail = detail
        super().__init__(f"API error {status}: {detail}")


class ApiClient:
    """Async HTTP client for Business OS Backend API."""
    
    def __init__(self, token: str | None = None):
        self.token = token
        self._session: aiohttp.ClientSession | None = None
    
    async def __aenter__(self) -> "ApiClient":
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        self._session = aiohttp.ClientSession(
            base_url=settings.API_URL,
            headers=headers,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session:
            await self._session.close()
            self._session = None
    
    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Make an HTTP request and return JSON response."""
        if not self._session:
            raise RuntimeError("ApiClient session not started. Use 'async with'.")
        
        async with self._session.request(method, path, **kwargs) as resp:
            if resp.status == 401:
                raise ApiAuthError()
            if resp.status >= 400:
                try:
                    detail = await resp.json()
                except Exception:
                    detail = await resp.text()
                raise ApiClientError(resp.status, detail)
            
            if resp.status == 204:
                return None
            
            try:
                return await resp.json()
            except Exception:
                return await resp.text()
    
    async def get(self, path: str, **kwargs: Any) -> Any:
        return await self.request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs: Any) -> Any:
        return await self.request("POST", path, **kwargs)
    
    async def put(self, path: str, **kwargs: Any) -> Any:
        return await self.request("PUT", path, **kwargs)
    
    async def delete(self, path: str, **kwargs: Any) -> Any:
        return await self.request("DELETE", path, **kwargs)
