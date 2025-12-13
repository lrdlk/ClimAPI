"""
BaseWeatherSource: clase base para integrar APIs meteorológicas.
Provee manejo de solicitudes HTTP con timeout, reintentos y logging.
"""
from __future__ import annotations

from typing import Dict, Any, Optional
import logging
import time

import requests

logger = logging.getLogger(__name__)


class BaseWeatherSource:
    """
    Clase base para fuentes de datos del clima.
    - Construcción segura de URLs
    - GET con timeout y reintentos
    - Manejo de errores estandarizado
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_seconds: float = 0.5,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.default_headers = default_headers or {
            "User-Agent": f"ClimAPI/{self.name}",
            "Accept": "*/*",
        }

    def build_url(self, endpoint: str) -> str:
        """Compone la URL absoluta para el endpoint dado."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        Ejecuta una solicitud GET con reintentos exponenciales.

        Args:
            endpoint: Ruta relativa o URL absoluta
            params: Parámetros de query
            headers: Headers adicionales

        Returns:
            requests.Response si la solicitud es exitosa.

        Raises:
            requests.HTTPError, requests.RequestException en fallos.
        """
        url = self.build_url(endpoint)
        params = params or {}
        req_headers = {**self.default_headers, **(headers or {})}

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"[{self.name}] GET {url} params={params} attempt={attempt}/{self.max_retries}"
                )
                resp = requests.get(url, params=params, headers=req_headers, timeout=self.timeout)
                resp.raise_for_status()
                return resp
            except requests.HTTPError as http_err:
                logger.warning(f"[{self.name}] HTTP {resp.status_code} en {url}: {http_err}")
                last_exc = http_err
            except requests.RequestException as req_err:
                logger.warning(f"[{self.name}] Error de request en {url}: {req_err}")
                last_exc = req_err

            if attempt < self.max_retries:
                time.sleep(self.retry_backoff_seconds * attempt)

        # Si agotó reintentos
        logger.error(f"[{self.name}] Fallo tras {self.max_retries} intentos: {last_exc}")
        if last_exc:
            raise last_exc
        raise requests.RequestException(f"[{self.name}] Solicitud fallida: {url}")
