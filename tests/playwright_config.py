"""Playwright test configuration for Reflex."""
import asyncio
import subprocess
import time
import httpx
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ReflexTestServer:
    """Manage Reflex server for E2E tests."""

    def __init__(self, mode="hybrid", port=3000):
        self.mode = mode
        self.port = port
        self.backend_port = 8000
        self.process = None
        self.ready = False

    def start(self, timeout=60):
        """Start Reflex server and wait for ready."""
        import os
        env = os.environ.copy()
        env["APP_MODE"] = self.mode
        env["DATABASE_URL"] = "sqlite:///./test_e2e.db"
        env["APP_ENV"] = "testing"

        logger.info(f"Starting Reflex in {self.mode} mode...")

        # Start reflex run
        self.process = subprocess.Popen(
            ["reflex", "run", "--loglevel", "warning"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for both servers to be ready
        start_time = time.time()
        backend_ready = False
        frontend_ready = False

        while time.time() - start_time < timeout:
            try:
                # Check backend
                if not backend_ready:
                    response = httpx.get(f"http://localhost:{self.backend_port}/docs", timeout=2)
                    if response.status_code == 200:
                        backend_ready = True
                        logger.info("✅ Backend ready")

                # Check frontend
                if not frontend_ready:
                    response = httpx.get(f"http://localhost:{self.port}", timeout=2)
                    if response.status_code == 200:
                        frontend_ready = True
                        logger.info("✅ Frontend ready")

                if backend_ready and frontend_ready:
                    self.ready = True
                    logger.info("✅ Reflex server fully ready")
                    time.sleep(2)  # Extra wait for hydration
                    return True

            except (httpx.ConnectError, httpx.ReadTimeout):
                pass

            time.sleep(0.5)

        raise TimeoutError(f"Reflex server failed to start within {timeout}s")

    def stop(self):
        """Stop Reflex server."""
        if self.process:
            logger.info("Stopping Reflex server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            logger.info("✅ Server stopped")

        # Cleanup test database
        import os
        try:
            os.unlink("test_e2e.db")
        except FileNotFoundError:
            pass
