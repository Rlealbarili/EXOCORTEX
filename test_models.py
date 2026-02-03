import subprocess
import urllib.request
import json

PROJECTS = [
    "gen-lang-client-0292562618",
    "gemini-cli-project-474614",
    "cogeplearning",
    "chrome-lane-457612-a1",
    "integracao-n8n-ads"
]
REGION = "us-central1"
MODELS = ["gemini-1.5-pro-001", "gemini-1.0-pro-001"]

def get_token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token", "--quiet"], shell=True).decode('utf-8').strip()

token = get_token()

for max_proj in PROJECTS:
    print(f"--- Checking Project: {max_proj} ---")
    for model in MODELS:
        url = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{max_proj}/locations/{REGION}/publishers/google/models/{model}:generateContent"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data = {"contents": [{"role": "user", "parts": [{"text": "Ping"}]}]}
        
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req) as response:
                print(f"[SUCCESS] Found working pair: Project={max_proj} / Model={model}")
                exit(0) # Found one!
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"[404] {model} not found in {max_proj}")
            elif e.code == 403:
                print(f"[403] Permission denied for {max_proj} (API disabled?)")
            else:
                print(f"[{e.code}] Error in {max_proj}")
        except Exception as e:
            print(f"[ERR] {e}")
