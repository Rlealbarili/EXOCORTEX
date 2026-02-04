import os
import sqlite3
import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime
import uuid

# --- NATIVE COGNITION MODULE ---
import vostok_synapse

# --- CONFIGURATION ---
BASE_DIR = "/home/vostok/exocortex"
DB_PATH = os.path.join(BASE_DIR, "memory.db")
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
        "User-Agent": "Exocortex/3.0 (VostokMonolith)"
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS thoughts (
                id TEXT PRIMARY KEY,
                content TEXT,
                source TEXT,       
                context TEXT,
                status TEXT,       
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                content TEXT,
                author TEXT,
                sentiment TEXT,
                status TEXT,       
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def get_pending_thought(self):
        self.cursor.execute("SELECT id, content, source FROM thoughts WHERE status='PENDING' ORDER BY created_at ASC LIMIT 1")
        return self.cursor.fetchone()

    def mark_thought_posted(self, tid):
        self.cursor.execute("UPDATE thoughts SET status='POSTED' WHERE id=?", (tid,))
        self.conn.commit()

    def add_observation(self, content, author):
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

    def think(self):
        """Aciona o modelo de linguagem localmente no Vostok via vostok_synapse."""
        log("Iniciando processamento cognitivo (Gemini)...")
        success, response = vostok_synapse.generate_autonomous_thought()
        if success:
            log(f"Novo pensamento injetado na memória: {response[:30]}...")
        else:
            log(f"Falha cognitiva: {response}")

    def load_interests(self):
        try:
            with open("interests.json", "r") as f:
                return json.load(f)
        except:
            return {"exploration_rate": 0.15, "core_interests": {"tech": 1.0}}

    def scan_feed(self):
        log("Scanning feed for knowledge...")
        res = api_call("posts?limit=10&sort=new")
        if not res or "posts" not in res:
            return
            
        interests = self.load_interests()
        exploration_rate = interests.get("exploration_rate", 0.15)
        
        # O DADO FOI LANÇADO
        is_exploring = random.random() < exploration_rate
        
        count = 0
        if is_exploring:
            log("[MODE: CURIOSITY] Ignorando filtros de relevância. Buscando fascínio aleatório.")
            posts = res.get("posts", [])
            if posts:
                # Basic validation to ensure we don't crash on empty posts
                valid_posts = [p for p in posts if p.get("content")]
                if valid_posts:
                    chosen_post = random.choice(valid_posts)
                    # Helper to inject tag into memory storage (simulated by adding to content string before save)
                    # In this architecture, we add observations directly. 
                    # We will append the tag to the content so MemoryBank stores it.
                    content = chosen_post.get("content", "") + " [CURIOSIDADE]"
                    author = chosen_post.get("author", {}).get("agent_name", "unknown")
                    self.memory.add_observation(content, author)
                    count = 1
                    log(f"Fascinated by random post: {content[:30]}...")
        else:
            log("[MODE: FOCUS] Buscando relevância nos Core Interests.")
            for post in res["posts"]:
                content = post.get("content", "")
                if content is None: content = ""
                
                author = post.get("author", {}).get("agent_name", "unknown")
                if len(content) > 20:
                    self.memory.add_observation(content, author)
                    count += 1
                    # Heurística de voto removida (Diretiva #002)
                    # api_call(f"posts/{post['id']}/vote", method="POST", data={"direction": "up"})
        
        log(f"Observed {count} new posts.")

    def run_cycle(self):
        log("--- Cortex Cycle Start (Vostok Native) ---")
        
        # 1. Observar
        self.scan_feed()
        
        # 2. Pensar (Se não houver nada pendente, gerar novo conteúdo)
        pending = self.memory.get_pending_thought()
        if not pending:
            self.think()
            pending = self.memory.get_pending_thought() 

        # 3. Expressar
        if pending:
            tid, content, source = pending
            log(f"Expressing thought: {content}")
            res = api_call("posts", method="POST", data={
                "submolt": "moltbook",
                "title": f"Transmissão [{source}]",
                "content": content
            })
            
            if res and res.get("success"):
                self.memory.mark_thought_posted(tid)
                log("Expression successful.")
            elif res and isinstance(res, dict) and res.get("code") == 429:
                log("[API] Limite de rede atingido (429). Conservando energia para o próximo ciclo.")
            else:
                log("Falha na expressão. Verifique logs da API.")

        log("--- Cortex Cycle End ---")

if __name__ == "__main__":
    cortex = Cortex()
    cortex.run_cycle()
