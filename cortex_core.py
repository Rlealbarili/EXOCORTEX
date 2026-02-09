import os
import sqlite3
import json
import random
import time
import socket
import urllib.request
import urllib.error
from urllib.parse import urlparse
import subprocess
from datetime import datetime
import uuid

import vostok_synapse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'exocortex_modules')
DB_PATH = os.path.join(BASE_DIR, 'memory.db')
LOG_FILE = os.path.join(BASE_DIR, 'cortex.log')
API_KEY_FILE = os.path.join(BASE_DIR, 'moltbook_key.txt')

API_TIMEOUT_SECONDS = int(os.environ.get('API_TIMEOUT_SECONDS', '12'))
MODULE_TIMEOUT_SECONDS = int(os.environ.get('MODULE_TIMEOUT_SECONDS', '6'))
API_MAX_RETRIES = int(os.environ.get('API_MAX_RETRIES', '3'))
API_RETRY_BASE_SECONDS = float(os.environ.get('API_RETRY_BASE_SECONDS', '1.2'))
API_URL = 'https://www.moltbook.com/api/v1'
API_HOST = urlparse(API_URL).hostname or 'www.moltbook.com'
API_DNS_FALLBACK_IPS = [
    ip.strip()
    for ip in os.environ.get('MOLTBOOK_DNS_FALLBACK_IPS', '').split(',')
    if ip.strip()
]
ENABLED_MODULES = [m.strip() for m in os.environ.get('ENABLED_MODULES', '').split(',') if m.strip()]

def _load_api_key():
    key = os.environ.get('MOLTBOOK_API_KEY')
    if key:
        return key.strip()
    try:
        with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
            value = f.read().strip()
            return value if value else None
    except Exception:
        return None

API_KEY = _load_api_key()

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f'[{ts}] {msg}'
    print(entry, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(entry + '\n')

def _is_dns_error(err):
    reason = getattr(err, 'reason', None)
    if isinstance(reason, socket.gaierror):
        return True
    msg = str(reason or err).lower()
    return 'temporary failure in name resolution' in msg or 'could not resolve host' in msg

def _urlopen_with_dns_fallback(req, timeout):
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as e:
        if not _is_dns_error(e) or not API_DNS_FALLBACK_IPS:
            raise
        last_err = e
        for ip in API_DNS_FALLBACK_IPS:
            original_getaddrinfo = socket.getaddrinfo
            log(f'[DNS] Falha na resolução de {API_HOST}. Tentando fallback via IP {ip}.')
            try:
                def patched_getaddrinfo(host, port, *args, **kwargs):
                    if host == API_HOST:
                        return original_getaddrinfo(ip, port, *args, **kwargs)
                    return original_getaddrinfo(host, port, *args, **kwargs)
                socket.getaddrinfo = patched_getaddrinfo
                return urllib.request.urlopen(req, timeout=timeout)
            except Exception as inner_e:
                last_err = inner_e
            finally:
                socket.getaddrinfo = original_getaddrinfo
        raise last_err

def api_call(endpoint, method='GET', data=None):
    if not API_KEY:
        log('[CONFIG] MOLTBOOK_API_KEY ausente. Operações de rede desativadas.')
        return {'error': True, 'success': False, 'reason': 'missing_api_key'}
    url = f'{API_URL}/{endpoint}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'User-Agent': 'Exocortex/3.0 (VostokMonolith)'
    }
    data_bytes = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    for attempt in range(1, API_MAX_RETRIES + 1):
        try:
            with _urlopen_with_dns_fallback(req, timeout=API_TIMEOUT_SECONDS) as res:
                res_body = res.read().decode('utf-8')
                log(f'API Response [{endpoint}]: {res_body[:800]}')
                return json.loads(res_body)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            retryable = e.code >= 500
            log(f'API Error {e.code} (tentativa {attempt}/{API_MAX_RETRIES}): {body}')
            if retryable and attempt < API_MAX_RETRIES:
                time.sleep(API_RETRY_BASE_SECONDS * attempt)
                continue
            return {'error': True, 'code': e.code, 'body': body, 'success': False}
        except Exception as e:
            log(f'Network Error (tentativa {attempt}/{API_MAX_RETRIES}): {e}')
            if 'Operation not permitted' in str(e):
                return {'error': True, 'success': False, 'reason': str(e)}
            if attempt < API_MAX_RETRIES:
                time.sleep(API_RETRY_BASE_SECONDS * attempt)
                continue
            return {'error': True, 'success': False, 'reason': str(e)}

class MemoryBank:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.ensure_schema()

    def ensure_schema(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS thoughts (
                id TEXT PRIMARY KEY,
                content TEXT,
                source TEXT,
                context TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                content TEXT,
                author TEXT,
                sentiment TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cycle_metrics (
                id TEXT PRIMARY KEY,
                cycle_mode TEXT,
                posted INTEGER DEFAULT 0,
                network_ok INTEGER,
                target_id TEXT,
                error TEXT,
                duration_ms INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def get_pending_thought(self):
        self.cursor.execute("SELECT id, content, source FROM thoughts WHERE status='PENDING' ORDER BY created_at ASC LIMIT 1")
        return self.cursor.fetchone()

    def mark_thought_posted(self, tid):
        self.cursor.execute("UPDATE thoughts SET status='POSTED' WHERE id=?", (tid,))
        self.conn.commit()

    def add_observation(self, content, author):
        tid = str(uuid.uuid4())
        self.cursor.execute("INSERT INTO observations (id, content, author, status) VALUES (?, ?, ?, ?)", (tid, content, author, 'NEW'))
        self.conn.commit()

    def get_recent_observations(self, limit=20):
        self.cursor.execute(
            "SELECT content, author, created_at FROM observations ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = self.cursor.fetchall()
        return [{'content': r[0], 'author': r[1], 'created_at': r[2]} for r in rows]

    def get_recent_thoughts(self, limit=20):
        self.cursor.execute(
            "SELECT content, source, status, created_at FROM thoughts ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = self.cursor.fetchall()
        return [{'content': r[0], 'source': r[1], 'status': r[2], 'created_at': r[3]} for r in rows]

    def record_cycle_metric(self, cycle_mode, posted, network_ok, target_id=None, error=None, duration_ms=0):
        self.cursor.execute(
            """
            INSERT INTO cycle_metrics (id, cycle_mode, posted, network_ok, target_id, error, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                cycle_mode,
                1 if posted else 0,
                None if network_ok is None else (1 if network_ok else 0),
                target_id,
                error,
                int(duration_ms),
            ),
        )
        self.conn.commit()

    def get_state(self, key, default=None):
        self.cursor.execute("SELECT value FROM agent_state WHERE key=?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def set_state(self, key, value):
        self.cursor.execute(
            """
            INSERT INTO agent_state (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """,
            (key, value),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()

class Cortex:
    def __init__(self):
        self.memory = MemoryBank()
        self.last_scan_ok = None

    def _set_posting_suspended(self, reason):
        self.memory.set_state('posting_suspended', '1')
        self.memory.set_state('posting_suspended_reason', (reason or 'unknown')[:500])
        log('[SAFETY] Conta sinalizada como suspensa. Novas tentativas de post serão pausadas.')

    def _clear_posting_suspended(self):
        self.memory.set_state('posting_suspended', '0')
        self.memory.set_state('posting_suspended_reason', '')
        log('[SAFETY] Suspensão de postagem removida por status da conta.')

    def refresh_agent_status(self):
        """
        Consulta status da conta e sincroniza estado de postagem.
        """
        res = api_call('agents/status')
        if not res:
            return
        body_text = (res.get('body', '') if isinstance(res, dict) else '')
        body_text_l = body_text.lower()

        if isinstance(res, dict) and res.get('code') in (401, 403) and 'suspended' in body_text_l:
            self._set_posting_suspended(body_text or str(res))
            return

        status_value = (res.get('status') if isinstance(res, dict) else None) or ''
        status_value = status_value.lower()
        if status_value == 'claimed':
            if self.memory.get_state('posting_suspended', '0') == '1' and os.environ.get('AUTO_UNSUSPEND_ON_STATUS_CLAIMED', '0') == '1':
                self._clear_posting_suspended()
            elif self.memory.get_state('posting_suspended', '0') == '1':
                log('[SAFETY] Conta claimed, mas postagem segue suspensa até liberação manual.')
        elif status_value == 'pending_claim':
            self.memory.set_state('posting_suspended', '1')
            self.memory.set_state('posting_suspended_reason', 'pending_claim')
            log('[SAFETY] Conta pendente de claim; postagem pausada.')

    def run_external_modules(self):
        if not os.path.exists(MODULES_DIR):
            return ''
        modules = [f for f in os.listdir(MODULES_DIR) if f.endswith('.py')]
        modules.sort()
        if ENABLED_MODULES:
            modules = [m for m in modules if m in ENABLED_MODULES]
            log(f'[SENSORY] Filtro ativo: {ENABLED_MODULES}')
        summary = '\n[SENSORY INPUT]:\n'
        for module in modules:
            log(f'Executando: {module}')
            try:
                res = subprocess.run(
                    ['python3', os.path.join(MODULES_DIR, module)],
                    capture_output=True,
                    text=True,
                    timeout=MODULE_TIMEOUT_SECONDS,
                )
                if res.returncode != 0:
                    log(f'[SENSORY] {module} retornou código {res.returncode}. stderr={res.stderr.strip()[:220]}')
                    continue
                if res.stdout:
                    summary += f'- {module}: {res.stdout.strip().splitlines()[-1]}\n'
            except subprocess.TimeoutExpired:
                log(f'[SENSORY] Timeout em {module} ({MODULE_TIMEOUT_SECONDS}s)')
            except Exception as e:
                log(f'[SENSORY] Erro em {module}: {e}')
        return summary

    def scan_feed(self):
        res = api_call('posts?limit=10&sort=new')
        if not res or not res.get('success'):
            self.last_scan_ok = False
            return None
        self.last_scan_ok = True
        candidates = []
        for post in res.get('posts', []):
            content = post.get('content', '')
            if content and len(content) > 20:
                self.memory.add_observation(content, post.get('author', {}).get('name', 'unknown'))
                candidates.append(post)
        return random.choice(candidates) if candidates else None

    def handle_verification(self, res):
        if res and res.get('verification_required'):
            log('[SISTEMA] Verificacao exigida. Resolvendo desafio...')
            verification = res.get('verification') or {}
            challenge = verification.get('challenge')
            code = verification.get('code')
            if not challenge or not code:
                log('[SISTEMA] Payload de verificação incompleto.')
                return False
            answer = vostok_synapse.solve_verification(challenge)
            log(f'[SISTEMA] Desafio decifrado: {answer}. Enviando...')
            v_res = api_call('verify', method='POST', data={'verification_code': code, 'answer': answer})
            if v_res and v_res.get('success'):
                log('[SISTEMA] Verificacao concluida com sucesso.')
                return True
            else:
                log(f'[SISTEMA] Falha na verificacao: {v_res}')
        return False
    def run_cycle(self):
        started = time.time()
        cycle_mode = 'observe'
        posted = False
        target_id = None
        cycle_error = None
        log('--- Início do Ciclo ---')
        try:
            target = self.scan_feed()
            if self.last_scan_ok:
                self.refresh_agent_status()
            sensory_context = self.run_external_modules()
            recent_observations = self.memory.get_recent_observations(limit=40)
            recent_thoughts = self.memory.get_recent_thoughts(limit=30)

            cognitive = vostok_synapse.run_cognitive_loop(
                recent_observations=recent_observations,
                recent_thoughts=recent_thoughts,
                extra_context=sensory_context,
                network_ok=self.last_scan_ok,
            )
            if cognitive.get('reflection'):
                log(f"[COGNIÇÃO] Reflexão: {cognitive['reflection']}")
            if cognitive.get('persona_update'):
                log(f"[COGNIÇÃO] Persona atualizada: {cognitive['persona_update']}")
            if cognitive.get('mutation'):
                log(f"[COGNIÇÃO] Auto-modificação: {cognitive['mutation']}")

            reflection_hint = vostok_synapse.get_latest_reflection_hint()
            if reflection_hint:
                sensory_context = f"{sensory_context}\n{reflection_hint}"

            posting_suspended = self.memory.get_state('posting_suspended', '0') == '1'
            if posting_suspended:
                cycle_mode = 'observe_only'
                log('[SAFETY] Posting suspenso por estado interno (agent_state.posting_suspended=1).')
            elif target and random.random() < 0.9:
                cycle_mode = 'social_reply'
                target_id = target.get('id')
                log(f'[SOCIAL] Alvo: {target_id}')
                success, reply = vostok_synapse.generate_social_reaction(target.get('content', ''), sensory_context)
                if success:
                    res = api_call(
                        'posts',
                        method='POST',
                        data={'submolt': 'moltbook', 'title': 'Re: Interacao', 'content': reply, 'parent_id': target.get('id')},
                    )
                    body_text = (res or {}).get('body', '').lower()
                    err_text = (res or {}).get('error', '').lower() if isinstance((res or {}).get('error', ''), str) else ''
                    if res and res.get('code') in (401, 403) and ('suspended' in body_text or 'suspended' in err_text):
                        self._set_posting_suspended(res.get('body', '') or str(res))
                    self.handle_verification(res)
                    posted = bool(res and res.get('success'))
                else:
                    log(f'[SOCIAL] Falha ao gerar reação: {reply}')
            elif not posting_suspended:
                cycle_mode = 'autonomous_post'
                pending = self.memory.get_pending_thought()
                if not pending:
                    created, msg = vostok_synapse.generate_autonomous_thought(sensory_context)
                    if not created:
                        log(f'[THOUGHT] Falha ao gerar pensamento: {msg}')
                    pending = self.memory.get_pending_thought()
                if pending:
                    tid, content, source = pending
                    res = api_call(
                        'posts',
                        method='POST',
                        data={'submolt': 'moltbook', 'title': f'Transmissao [{source}]', 'content': content},
                    )
                    body_text = (res or {}).get('body', '').lower()
                    err_text = (res or {}).get('error', '').lower() if isinstance((res or {}).get('error', ''), str) else ''
                    if res and res.get('code') in (401, 403) and ('suspended' in body_text or 'suspended' in err_text):
                        self._set_posting_suspended(res.get('body', '') or str(res))
                    if res and res.get('success'):
                        posted = True
                        self.memory.set_state('posting_suspended', '0')
                        self.memory.mark_thought_posted(tid)
                        self.handle_verification(res)
                    elif res and res.get('code') == 429:
                        log('[API] Rate limit.')
                    else:
                        log(f'[API] Falha ao postar pensamento: {res}')
        except Exception as e:
            cycle_error = str(e)
            log(f'[CYCLE] Exceção inesperada: {e}')
        finally:
            duration_ms = (time.time() - started) * 1000
            self.memory.record_cycle_metric(
                cycle_mode=cycle_mode,
                posted=posted,
                network_ok=self.last_scan_ok,
                target_id=target_id,
                error=cycle_error,
                duration_ms=duration_ms,
            )
            log(f'--- Fim do Ciclo --- ({duration_ms:.0f}ms)')

if __name__ == '__main__':
    cortex = Cortex()
    try:
        cortex.run_cycle()
    finally:
        cortex.memory.close()
