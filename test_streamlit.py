#!/usr/bin/env python3
import subprocess
import time
import requests
import signal
import os

def test_streamlit_startup():
    """Test that Streamlit app starts successfully"""
    print("🚀 Testing Streamlit app startup...")
    
    # Start Streamlit
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    
    print("⏳ Waiting for app to start...")
    
    # Wait for app to start
    max_retries = 30
    base_url = "http://localhost:8501"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Streamlit app started successfully on {base_url}")
                print(f"📄 Page title: {response.text[:200]}...")
                break
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                print("❌ Failed to start Streamlit app")
                return False
    else:
        print("❌ Streamlit app failed to start")
        return False
    
    # Test health check
    try:
        health_response = requests.get(f"{base_url}/healthz", timeout=5)
        print(f"🏥 Health check: {health_response.status_code}")
    except:
        print("⚠️ Health check endpoint not available (normal for Streamlit)")
    
    # Cleanup
    try:
        if hasattr(os, 'killpg'):
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=10)
        print("🧹 Cleanup completed")
    except:
        if hasattr(os, 'killpg'):
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        else:
            process.kill()
    
    return True

if __name__ == "__main__":
    success = test_streamlit_startup()
    exit(0 if success else 1)