import subprocess

HOST = "vostok@100.69.70.3"
SQL = "UPDATE thoughts SET status='SKIPPED' WHERE status='PENDING' AND content LIKE 'ARCHITECTURAL%';"

cmd = [
    "ssh", "-o", "StrictHostKeyChecking=no", HOST,
    f"python3 -c \"import sqlite3; conn = sqlite3.connect('/home/vostok/exocortex/memory.db'); cursor = conn.cursor(); cursor.execute(\\\"{SQL}\\\"); conn.commit(); print('Fixed.');\""
]

print(f"Executing: {' '.join(cmd)}")
try:
    subprocess.check_call(cmd)
    print("SUCCESS: Database updated.")
except subprocess.CalledProcessError as e:
    print(f"FAIL: {e}")
