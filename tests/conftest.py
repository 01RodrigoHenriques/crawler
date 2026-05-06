"""Shared pytest fixtures for integration and regression tests."""

import pytest

import session as session_module


@pytest.fixture(autouse=True)
def reset_shared_session():
    """Ensure the global HTTP session does not leak between tests."""
    if session_module._session is not None:
        session_module._session.close()
    session_module._session = None

    yield

    if session_module._session is not None:
        session_module._session.close()
    session_module._session = None
