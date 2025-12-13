"""
BaseWeatherSource: clase base para fuentes meteorológicas.
Proporciona utilidades comunes como manejo de API key y requests con reintentos.
"""

from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseWeatherSource:
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

        self._session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        self._session.mount("https://", HTTPAdapter(max_retries=retries))
        self._session.mount("http://", HTTPAdapter(max_retries=retries))

    def _make_request(self, endpoint: str, params: Optional[dict] = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self._session.get(url, params=params or {}, timeout=self.timeout)
        response.raise_for_status()
        return response
