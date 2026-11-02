"""Independent CLI diagnostic tool for xAI Grok API configuration and connectivity.

Run via:
    python test_grok.py
"""
import os
import sys
import time
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

# Load .env explicitly
load_dotenv(backend_dir / ".env")

from app.core.config import settings
from app.services.grok_service import grok_service


def run_diagnostic():
    print("=" * 60)
    print("             ARI -- GROK API INDEPENDENT DIAGNOSTIC")
    print("=" * 60)

    # 1. Environment Configuration check
    env_file_exists = (backend_dir / ".env").exists()
    env_status = "PASS" if env_file_exists else "FAIL"

    # 2. API Key check
    key = settings.XAI_API_KEY
    has_key = bool(settings.is_grok_configured)
    key_display = "YES" if has_key else "NO"

    # Print initial results
    print(f"Environment configuration: {env_status}")
    print(f"API key available:         {key_display}")
    print(f"Target model:              {settings.GROK_MODEL}")
    print(f"API Base URL:              {settings.XAI_BASE_URL}")
    print("-" * 60)

    if not has_key:
        print("API authentication:        FAIL (No valid key in .env)")
        print("Model availability:        FAIL (Skipped due to missing key)")
        print("Test generation:           FAIL (Skipped due to missing key)")
        print("=" * 60)
        print("DIAGNOSTIC RESULT: FAIL")
        print("\nACTION REQUIRED:")
        print("1. Open backend/.env in an editor.")
        print("2. Set XAI_API_KEY=your_actual_xai_api_key")
        print("3. Re-run: python test_grok.py")
        print("=" * 60)
        return False

    # 3. Live API test
    print("Contacting official xAI Responses endpoint...")
    result = grok_service.test_connection()

    if result["success"]:
        print("API authentication:        PASS")
        print("Model availability:        PASS")
        print("Test generation:           PASS")
        print(f"Response latency:          {result.get('latency_ms', 'N/A')} ms")
        print("-" * 60)
        print("DIAGNOSTIC RESULT: ALL PASS")
        print("xAI Grok API is fully configured and operational!")
        print("=" * 60)
        return True
    else:
        status_code = result.get("status")
        auth_pass = "FAIL" if status_code in ["auth_failed", "not_configured"] else "PASS"
        model_pass = "FAIL" if status_code in ["model_not_found", "auth_failed"] else "PASS"

        print(f"API authentication:        {auth_pass}")
        print(f"Model availability:        {model_pass}")
        print("Test generation:           FAIL")
        print("-" * 60)
        print(f"Status:  {status_code}")
        print(f"Details: {result.get('message')}")
        print("=" * 60)
        print("DIAGNOSTIC RESULT: FAIL")
        return False


if __name__ == "__main__":
    success = run_diagnostic()
    sys.exit(0 if success else 1)
