import time
from typing import Iterable

from fastapi import Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware


REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ("method", "path", "status"),
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ("method", "path", "status"),
)
REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "Total HTTP requests that resulted in an error",
    ("method", "path"),
)


def resolve_path_template(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


def build_metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, skip_paths: Iterable[str] | None = None):
        super().__init__(app)
        self.skip_paths = set(skip_paths or [])

    async def dispatch(self, request: Request, call_next):
        path = resolve_path_template(request)
        if path in self.skip_paths:
            return await call_next(request)

        method = request.method
        start_time = time.perf_counter()
        status_code = "500"
        error_recorded = False

        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            return response
        except Exception:
            REQUEST_ERRORS.labels(method, path).inc()
            error_recorded = True
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            REQUEST_COUNTER.labels(method, path, status_code).inc()
            REQUEST_LATENCY.labels(method, path, status_code).observe(elapsed)

            if not error_recorded and int(status_code) >= 500:
                REQUEST_ERRORS.labels(method, path).inc()
