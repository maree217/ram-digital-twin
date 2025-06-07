import pytest
import subprocess
import time
import requests
import os
import signal
from playwright.sync_api import sync_playwright
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def streamlit_app():
    """Start Streamlit app for testing"""
    app_path = Path(__file__).parent / "streamlit_app.py"
    port = 8501
    
    # Start Streamlit app
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    process = subprocess.Popen(
        ["streamlit", "run", str(app_path), f"--server.port={port}", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    
    # Wait for app to start
    max_retries = 30
    base_url = f"http://localhost:{port}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                logger.info(f"Streamlit app started successfully on {base_url}")
                break
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                logger.error("Failed to start Streamlit app")
                raise
    else:
        raise RuntimeError("Streamlit app failed to start")
    
    yield {"process": process, "base_url": base_url}
    
    # Cleanup
    try:
        if hasattr(os, 'killpg'):
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=10)
    except (subprocess.TimeoutExpired, ProcessLookupError):
        if hasattr(os, 'killpg'):
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        else:
            process.kill()

@pytest.fixture
def page(streamlit_app, playwright):
    """Create a new page for each test"""
    browser = playwright.chromium.launch(
        headless=True,
        args=['--disable-dev-shm-usage', '--no-sandbox']
    )
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    # Navigate to Streamlit app
    page.goto(streamlit_app["base_url"])
    
    # Wait for Streamlit to load
    page.wait_for_selector('[data-testid="stApp"]', timeout=30000)
    
    # Wait for any initial loading to complete
    page.wait_for_timeout(2000)
    
    yield page
    
    context.close()
    browser.close()

@pytest.fixture
def api_mocker():
    """Helper for API mocking"""
    class APIMocker:
        def __init__(self):
            self.mocked_routes = {}
        
        def mock_endpoint(self, page, url_pattern, response_data, status=200):
            def handle_request(route):
                route.fulfill(
                    status=status,
                    content_type="application/json",
                    body=response_data if isinstance(response_data, str) else str(response_data)
                )
            
            page.route(url_pattern, handle_request)
            self.mocked_routes[url_pattern] = response_data
        
        def mock_gemini_api(self, page, response_text="This is a mocked response from Ram's expertise."):
            """Mock Gemini AI API calls"""
            self.mock_endpoint(
                page,
                "**/v1beta/models/gemini-*:generateContent",
                f'{{"candidates": [{{"content": {{"parts": [{{"text": "{response_text}"}}]}}}}]}}',
                200
            )
    
    return APIMocker()

@pytest.fixture
def mock_knowledge_base():
    """Mock knowledge base responses"""
    return {
        "pmo": "PMO setup experience includes governance frameworks and resource optimization",
        "dynamics": "Dynamics 365 implementation with custom workflows and integrations",
        "transformation": "Digital transformation strategies for public sector organizations",
        "housing": "Housing association modernization with tenant satisfaction improvements"
    }