import urllib.request
import json
import ssl

KEY = "REVOKED_GOOGLE_API_KEY"
URL = f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}"

try:
    # SSL context to avoid certificate issues on some Windows setups
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(URL, context=ctx) as response:
        data = json.load(response)
        if "models" in data:
            print("--- Available Models ---")
            for m in data["models"]:
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    print(m["name"])
        else:
            print("No models found.")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
