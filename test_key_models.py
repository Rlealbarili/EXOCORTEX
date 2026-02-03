import urllib.request
import json
import ssl

KEY = "REVOKED_GOOGLE_API_KEY"
MODELS = [
    "gemini-1.5-pro-latest",
    "gemini-1.5-pro",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-pro"
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for m in MODELS:
    print(f"Testing {m}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": "Ping"}]}]}
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
        with urllib.request.urlopen(req, context=ctx) as response:
            print(f"[SUCCESS] {m} works!")
            break
    except urllib.error.HTTPError as e:
        print(f"[FAIL] {m}: {e.code}")
    except Exception as e:
        print(f"[ERR] {e}")
