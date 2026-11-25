import os
import pytest
from app.main import app

os.environ["TESTING"] = "true"

@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """Ensure limiter is disabled during unit/integration tests."""
    app.state.limiter.enabled = False
    yield
    app.state.limiter.enabled = False
