"""API Client Utility"""
import logging
from urllib.parse import urljoin
from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)


class LoggingRetry(Retry):
    """Retry Logger Adapter"""

    def get_backoff_time(self):
        if self.history:
            last = self.history[-1]
            if hasattr(last, "response") and last.response is not None:
                retry_after = last.response.headers.get("Retry-After")
                if retry_after is not None:
                    return float(retry_after)
        return super().get_backoff_time()

    def increment(self, *args, **kwargs):
        new_retry = super().increment(*args, **kwargs)
        if new_retry.history:
            last = new_retry.history[-1]
            logger.warning(
                "Retrying %s : %s after status: %s error: %s Retry: %s/%s",
                last.method,
                last.url,
                last.status,
                last.error,
                len(new_retry.history),
                self.total
            )
        return new_retry


class APIClient(requests.Session):
    """Custom API client for building URLs and logging requests/responses."""

    def __init__(self, base_url: str, base_path: str = "", headers: dict = None):
        super().__init__()
        self.base_url = base_url.rstrip("/") + "/"
        self.base_path = base_path.rstrip("/") + "/" if base_path else ""
        self.headers.update(headers or {})
        self.hooks['response'].append(self.log_response)
        retries = LoggingRetry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS",
                             "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.mount("https://", adapter)
        self.mount("http://", adapter)

    def build_url(self, endpoint: str = None) -> str:
        """Build a full URL for the given endpoint."""
        endpoint = endpoint.lstrip("/") if endpoint else ""
        fullpath = f'{self.base_path}{endpoint}'
        return urljoin(self.base_url, fullpath)

    def log_response(self, response: requests.Response, *args, **kwargs):
        """Log details of the request and response."""
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Body: %s", response.request.body)
        logger.info("%s : %s -> %s", response.request.method,
                    response.request.url, response.status_code)
        logger.debug("Response Headers: %s", response.headers)
        logger.debug("Response Body: %s", response.text)
        return response
