"""
Tests for the FastAPI health and root endpoints.

These are the simplest smoke tests to confirm the app boots
and responds to basic HTTP requests.
"""
import pytest


class TestHealthEndpoint:
    """Health check endpoint tests."""

    def test_health_returns_200(self, client):
        """The /crooked-finger/health endpoint returns 200 with expected body."""
        response = client.get("/crooked-finger/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"
        assert body["service"] == "crooked-finger"

    def test_root_returns_200(self, client):
        """The root endpoint returns service metadata."""
        response = client.get("/")
        assert response.status_code == 200
        body = response.json()
        assert "Crooked Finger" in body["message"]
        assert "graphql" in body["endpoints"]
