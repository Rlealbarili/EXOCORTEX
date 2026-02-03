import urllib.request
import json
import ssl

KEY = "REVOKED_GOOGLE_API_KEY"

# List of variations to try
ID = "gemini-pro"
URLS = [
    f"https://generativelanguage.googleapis.com/v1beta/models/{ID}:generateContent?key={KEY}",
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={KEY}",
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={KEY}",
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={KEY}"
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

data = {"contents": [{"parts": [{"text": "Ping"}]}]}

for url in URLS:
    print(f"Testing URL: {url.replace(KEY, 'HIDDEN_KEY')}")
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, context=ctx) as response:
            print(f"[SUCCESS] {response.getcode()}")
            print(response.read().decode('utf-8')[:100])
            break
    except urllib.error.HTTPError as e:
        print(f"[FAIL] {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
