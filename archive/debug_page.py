#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import subprocess
import time
import os
import signal

def debug_page_structure():
    """Debug the page structure to understand element layout"""
    # Start Streamlit
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app.py", "--server.port=8502"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    
    time.sleep(5)  # Wait for startup
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto("http://localhost:8502")
            page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
            
            print("🔍 Page Structure Analysis:")
            print(f"Title: {page.title()}")
            
            # Check all headings
            h1_elements = page.locator("h1").all()
            print(f"\n📝 H1 elements ({len(h1_elements)}):")
            for i, h1 in enumerate(h1_elements):
                print(f"  {i+1}. {h1.text_content()}")
            
            h3_elements = page.locator("h3").all()
            print(f"\n📝 H3 elements ({len(h3_elements)}):")
            for i, h3 in enumerate(h3_elements):
                print(f"  {i+1}. {h3.text_content()}")
            
            # Check for header content
            main_header = page.locator(".main-header")
            if main_header.is_visible():
                print(f"\n🎨 Main header content: {main_header.text_content()[:200]}...")
            
            # Check for welcome message
            welcome = page.locator(".assistant-message")
            if welcome.first.is_visible():
                print(f"\n👋 Welcome message: {welcome.first.text_content()[:100]}...")
            
            # Check for chat input
            chat_inputs = page.locator('input').all()
            print(f"\n💬 Input elements ({len(chat_inputs)}):")
            for i, inp in enumerate(chat_inputs):
                placeholder = inp.get_attribute("placeholder") or "No placeholder"
                print(f"  {i+1}. {placeholder}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            browser.close()
    
    # Cleanup
    try:
        if hasattr(os, 'killpg'):
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()
    except:
        pass

if __name__ == "__main__":
    debug_page_structure()