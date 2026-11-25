import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Disable rate limiting during automated test runs
is_testing = os.getenv("TESTING", "false").lower() in ("true", "1") or "pytest" in os.environ.get("_", "").lower()

limiter = Limiter(
    key_func=get_remote_address,
    enabled=not is_testing,
)
