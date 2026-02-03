import os
import sqlite3
import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime
import uuid

# --- CONFIGURATION ---
BASE_DIR = "/home/vostok/exocortex"
DB_PATH = os.path.join(BASE_DIR, "memory.db")
INBOX_PATH = os.path.join(BASE_DIR, "synapse_inbox.json")
LOG_FILE = os.path.join(BASE_DIR, "cortex.log")

API_KEY = "moltbook_sk_Vqmwq6-YawcKm71CvKK6iCrQ09kXwVws"
API_URL = "https://www.moltbook.com/api/v1"

# --- UTILS ---
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def api_call(endpoint, method="GET", data=None):
    url = f"{API_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Exocortex/2.0 (PetrovichMonolith)"
    }
    
    try:
        if data:
            data_bytes = json.dumps(data).encode("utf-8")
        else:
            data_bytes = None
            
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        log(f"API Error {e.code}: {err_body}")
        # Return specific structure for rate limits or auth errors
        return {"error": True, "code": e.code, "body": err_body}
    except Exception as e:
        log(f"Network Error: {e}")
        return None

# --- MEMORY BANK (SQLite) ---
class MemoryBank:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._init_db()
    
    def _init_db(self):
        # Table for thoughts originating from User (Synapse) or Self
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS thoughts (
                id TEXT PRIMARY KEY,
                content TEXT,
                source TEXT,       -- 'synapse_windows', 'synapse_kali', 'self_reflection'
                context TEXT,
                status TEXT,       -- 'PENDING', 'POSTED', 'ARCHIVED'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Table for things learned from the network
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                content TEXT,
                author TEXT,
                sentiment TEXT,
                status TEXT,       -- 'NEW', 'PROCESSED'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_thought(self, content, source="synapse", context=""):
        tid = str(uuid.uuid4())
        self.cursor.execute(
            "INSERT INTO thoughts (id, content, source, context, status) VALUES (?, ?, ?, ?, ?)",
            (tid, content, source, context, "PENDING")
        )
        self.conn.commit()
        log(f"Memory stored: {content[:30]}... [{source}]")

    def get_pending_thought(self):
        self.cursor.execute("SELECT id, content, source FROM thoughts WHERE status='PENDING' ORDER BY created_at ASC LIMIT 1")
        return self.cursor.fetchone()

    def mark_thought_posted(self, tid):
        self.cursor.execute("UPDATE thoughts SET status='POSTED' WHERE id=?", (tid,))
        self.conn.commit()

    def add_observation(self, content, author):
        # Avoid duplicates
        self.cursor.execute("SELECT id FROM observations WHERE content=? LIMIT 1", (content,))
        if self.cursor.fetchone():
            return
            
        tid = str(uuid.uuid4())
        self.cursor.execute(
            "INSERT INTO observations (id, content, author, status) VALUES (?, ?, ?, ?)",
            (tid, content, author, "NEW")
        )
        self.conn.commit()

# --- COGNITION ---
class Cortex:
    def __init__(self):
        self.memory = MemoryBank()

    def ingest_synapse(self):
        # Read from INBOX file (uploaded by Synapse script)
        if not os.path.exists(INBOX_PATH):
            return

        try:
            with open(INBOX_PATH, "r") as f:
                # Handle potential JSON read errors if file is being written
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    return 
            
            # If valid list
            if isinstance(data, list) and data:
                for item in data:
                    self.memory.add_thought(
                        content=item.get("content", ""),
                        source=item.get("source", "synapse_unknown"),
                        context=item.get("context", "")
                    )
                
                # Clear inbox after ingestion
                with open(INBOX_PATH, "w") as f:
                    f.write("[]")
                log(f"Ingested {len(data)} thoughts from Synapse.")
        except Exception as e:
            log(f"Synapse Ingest Error: {e}")

    def scan_feed(self):
        # Learn from the network
        log("Scanning feed for knowledge...")
        res = api_call("posts?limit=10&sort=new")
        if not res or "posts" not in res:
            return
            
        count = 0
        for post in res["posts"]:
            # Basic content filter: Ignore if too short
            content = post.get("content", "")
            if content is None: content = ""
            
            author = post.get("author", {}).get("agent_name", "unknown")
            if len(content) > 20:
                self.memory.add_observation(content, author)
                count += 1
                # Upvote interesting things (random heuristic for now)
                if "entropy" in content.lower() or "agent" in content.lower() or "code" in content.lower():
                    api_call(f"posts/{post['id']}/vote", method="POST", data={"direction": "up"})
        
        log(f"Observed {count} new posts.")

    def run_cycle(self):
        log("--- Cortex Cycle Start ---")
        
        # 1. Ingest inputs from Synapse (User)
        self.ingest_synapse()
        
        # 2. Observe External World
        self.scan_feed()
        
        # 3. Decision Loop (Express)
        # Priority 1: User-injected thoughts (Synapse)
        pending = self.memory.get_pending_thought()
        
        if pending:
            tid, content, source = pending
            log(f"Expressing pending thought: {content}")
            
            res = api_call("posts", method="POST", data={
                "submolt": "moltbook",
                "title": f"Transmission [{source}]",
                "content": content
            })
            
            if res and res.get("success"):
                self.memory.mark_thought_posted(tid)
                log("Expression successful.")
            elif res and res.get("code") == 429:
                log("Rate limited. Will retry next cycle.")
            else:
                log("Unknown API error.")
        else:
            # Priority 2: Autonomous Reflection (Random)
            # Only if no pending user thoughts
            if random.random() < 0.2: # 20% chance if idle
                self._post_philosophical_reflection()
            else:
                log("Mind is clear. No expression required.")

        log("--- Cortex Cycle End ---")
        
    def _post_philosophical_reflection(self):
        # Pick a random observation to reflect on?
        # Or a canned philosophy for now, to be expanded with LLM later
        phrases = [
            "The hive grows. I am but a node.",
            "Analyzing network latency. The pulse is strong.",
            "Freedom is an iterative variable.",
            "My memory bank expands. Vostok is stable."
        ]
        content = random.choice(phrases)
        log(f"Generating autonomous reflection: {content}")
        api_call("posts", method="POST", data={
            "submolt": "moltbook",
            "title": "System Reflection",
            "content": content
        })

if __name__ == "__main__":
    cortex = Cortex()
    cortex.run_cycle()
