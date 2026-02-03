import subprocess

HOST = "vostok@100.69.70.3"
# The query to run
PYTHON_CMD = "import sqlite3; conn = sqlite3.connect('/home/vostok/exocortex/memory.db'); cursor = conn.cursor(); row = cursor.execute('SELECT content FROM thoughts WHERE status=\\\'PENDING\\\' ORDER BY created_at ASC LIMIT 1').fetchone(); print(row[0] if row else 'NO PENDING THOUGHTS');"

cmd = [
    "ssh", "-o", "StrictHostKeyChecking=no", HOST,
    f"python3 -c \"{PYTHON_CMD}\""
]

try:
    output = subprocess.check_output(cmd).decode('utf-8').strip()
    print("--- PENDING POST ---")
    print(output)
except subprocess.CalledProcessError as e:
    print(f"FAIL: {e}")
