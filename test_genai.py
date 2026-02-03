import subprocess
import urllib.request
import json

def get_token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token", "--quiet"], shell=True).decode('utf-8').strip()

token = get_token()
print(f"Token acquired. Length: {len(token)}")

# Try Gemini Pro via Generative Language API
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "x-goog-user-project": "gemini-cli-project-474614" # Explicitly bill this project
}
data = {"contents": [{"parts": [{"text": "Hello, are you there?"}]}]}

try:
    print(f"Hitting {url}...")
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        res = getattr(response, 'read')().decode('utf-8')
        print("SUCCESS:")
        print(res[:200])
except Exception as e:
    print(f"FAIL: {e}")
    if hasattr(e, 'read'):
        try:
            print(e.read().decode('utf-8'))
        except:
            pass
