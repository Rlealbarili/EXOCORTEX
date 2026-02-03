import subprocess
import urllib.request
import json

PROJECT_ID = "gemini-cli-project-474614"
REGION = "us-central1"

def get_token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token", "--quiet"], shell=True).decode('utf-8').strip()

token = get_token()
url = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models"

req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(req) as response:
        data = json.load(response)
        if "models" in data:
            print("Available Models:")
            for m in data["models"]:
                if "gemini" in m["name"]:
                    print(f"- {m['name'].split('/')[-1]} ({m['versionId']})")
        else:
            print("No models found.")
except Exception as e:
    print(e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
