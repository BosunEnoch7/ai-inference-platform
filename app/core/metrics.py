from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests.",
    ("method", "path", "status_code"),
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "path"),
)
HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed.",
    ("method",),
)
INFERENCE_REQUESTS = Counter(
    "inference_requests_total",
    "Total inference requests by provider and outcome.",
    ("provider", "outcome"),
)
INFERENCE_DURATION = Histogram(
    "inference_duration_seconds",
    "Inference duration in seconds by provider.",
    ("provider",),
)
