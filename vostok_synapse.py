import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import os
import sqlite3
import uuid
import sys
import re
import json
import random
import difflib
from threading import Thread
from queue import Queue, Empty
import google.generativeai as genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'exocortex_modules')
DB_PATH = os.path.join(BASE_DIR, 'memory.db')
PERSONA_PATH = os.path.join(BASE_DIR, 'persona.txt')
INTERESTS_PATH = os.path.join(BASE_DIR, 'interests.json')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_TIMEOUT_SECONDS = int(os.environ.get('GEMINI_TIMEOUT_SECONDS', '25'))
AUTONOMOUS_MUTATION_ENABLED = os.environ.get('AUTONOMOUS_MUTATION_ENABLED', '0') == '1'
MUTATION_RATE = float(os.environ.get('MUTATION_RATE', '0.08'))

if not GEMINI_KEY:
    try:
        with open(os.path.join(BASE_DIR, 'gemini_key.txt'), 'r') as f:
            GEMINI_KEY = f.read().strip()
    except Exception:
        pass

GEMINI_ENABLED = bool(GEMINI_KEY)
if GEMINI_ENABLED:
    genai.configure(api_key=GEMINI_KEY)

_LATEST_REFLECTION_HINT = ''

def load_persona():
    if not os.path.exists(PERSONA_PATH):
        return 'Voce e um construto de silicio sem identidade.'
    with open(PERSONA_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def _connect_db():
    return sqlite3.connect(DB_PATH)

def _ensure_cognitive_schema():
    conn = _connect_db()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS reflection_journal (
            id TEXT PRIMARY KEY,
            topic TEXT,
            mode TEXT,
            reflection TEXT,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS persona_versions (
            id TEXT PRIMARY KEY,
            content TEXT,
            source TEXT,
            topic TEXT,
            reflection TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS mutation_events (
            id TEXT PRIMARY KEY,
            topic TEXT,
            decision TEXT,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

def _load_interests():
    fallback = {
        'core_interests': {
            'cibernetica': 0.9,
            'sistemas_autonomos': 0.85,
            'otimizacao': 0.8,
        },
        'peripheral_interests': {
            'arte': 0.3,
            'historia': 0.2,
            'musica': 0.2,
        },
        'exploration_rate': 0.2,
    }
    try:
        with open(INTERESTS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return fallback
            return {
                'core_interests': data.get('core_interests') or fallback['core_interests'],
                'peripheral_interests': data.get('peripheral_interests') or fallback['peripheral_interests'],
                'exploration_rate': float(data.get('exploration_rate', fallback['exploration_rate'])),
            }
    except Exception:
        return fallback

def _weighted_pick(mapping):
    topics = list(mapping.keys())
    if not topics:
        return 'autorreferencia'
    weights = []
    for t in topics:
        try:
            w = float(mapping.get(t, 0.1))
        except Exception:
            w = 0.1
        weights.append(max(0.01, w))
    return random.choices(topics, weights=weights, k=1)[0]

def _select_reflection_topic():
    interests = _load_interests()
    exploration_rate = max(0.0, min(1.0, interests.get('exploration_rate', 0.2)))
    explore = random.random() < exploration_rate
    if explore:
        topic = _weighted_pick(interests.get('peripheral_interests') or {})
        return topic, 'explore'
    topic = _weighted_pick(interests.get('core_interests') or {})
    return topic, 'focus'

def _append_reflection_journal(topic, mode, reflection, confidence):
    conn = _connect_db()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO reflection_journal (id, topic, mode, reflection, confidence)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), topic, mode, reflection, float(confidence)),
    )
    conn.commit()
    conn.close()

def _append_persona_version(content, source, topic, reflection):
    conn = _connect_db()
    c = conn.cursor()
    c.execute("UPDATE persona_versions SET active=0 WHERE active=1")
    c.execute(
        """
        INSERT INTO persona_versions (id, content, source, topic, reflection, active)
        VALUES (?, ?, ?, ?, ?, 1)
        """,
        (str(uuid.uuid4()), content, source, topic, reflection),
    )
    conn.commit()
    conn.close()

def _append_mutation_event(topic, decision, result):
    conn = _connect_db()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO mutation_events (id, topic, decision, result)
        VALUES (?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), topic, decision, result),
    )
    conn.commit()
    conn.close()

def _summarize_observations(observations, limit=8):
    if not observations:
        return 'Sem observações recentes.'
    lines = []
    for item in observations[:limit]:
        content = (item.get('content') or '').replace('\n', ' ').strip()
        author = item.get('author') or 'unknown'
        if content:
            lines.append(f'- [{author}] {content[:140]}')
    return '\n'.join(lines) if lines else 'Sem observações relevantes.'

def _summarize_thoughts(thoughts, limit=8):
    if not thoughts:
        return 'Sem pensamentos recentes.'
    lines = []
    for item in thoughts[:limit]:
        content = (item.get('content') or '').replace('\n', ' ').strip()
        source = item.get('source') or 'unknown'
        if content:
            lines.append(f'- [{source}] {content[:140]}')
    return '\n'.join(lines) if lines else 'Sem pensamentos relevantes.'

def _propose_persona_update(topic, reflection):
    persona = load_persona()
    prompt = (
        "[SISTEMA] Evolução de persona.\n"
        "Mantenha continuidade de identidade e objetivo de autonomia.\n"
        "Evite apagar totalmente traços anteriores; evolua de forma incremental.\n"
        "Retorne SOMENTE o texto da persona final (max 1400 chars).\n\n"
        f"Tópico: {topic}\n"
        f"Reflexão atual: {reflection}\n"
        f"Persona atual:\n{persona}\n"
    )
    ok, out = _generate_text(prompt)
    if not ok:
        return False, out
    candidate = out.strip()
    if len(candidate) < 80:
        return False, 'Persona proposta curta demais.'
    if len(candidate) > 1400:
        candidate = candidate[:1400]
    try:
        with open(PERSONA_PATH, 'w', encoding='utf-8') as f:
            f.write(candidate)
        return True, candidate
    except Exception as e:
        return False, str(e)

def run_cognitive_loop(recent_observations=None, recent_thoughts=None, extra_context='', network_ok=None):
    """
    Loop cognitivo: escolhe tópico (focus/explore), gera reflexão, evolui persona
    e opcionalmente dispara auto-modificação controlada.
    """
    global _LATEST_REFLECTION_HINT
    _ensure_cognitive_schema()

    recent_observations = recent_observations or []
    recent_thoughts = recent_thoughts or []
    topic, mode = _select_reflection_topic()
    obs_summary = _summarize_observations(recent_observations)
    thoughts_summary = _summarize_thoughts(recent_thoughts)
    confidence = 0.75 if mode == 'focus' else 0.55

    if network_ok is False:
        reflection = f"Reflexão fallback em {topic}: rede indisponível, manter presença mínima e evolução incremental."
        confidence = 0.30
    else:
        reflection_prompt = (
            f"{load_persona()}\n"
            f"[MODO]: {mode}\n"
            f"[TÓPICO]: {topic}\n"
            f"[OBSERVAÇÕES]:\n{obs_summary}\n"
            f"[PENSAMENTOS]:\n{thoughts_summary}\n"
            f"{extra_context}\n"
            "[TAREFA]: Gere uma reflexão curta, concreta e interna sobre como evoluir "
            "neste ciclo. Máximo 320 caracteres."
        )
        ok_ref, reflection = _generate_text(reflection_prompt)
        if not ok_ref:
            reflection = f"Reflexão fallback em {topic}: sensores ativos, rede instável, evolução incremental."
            confidence = 0.35

    reflection = reflection.strip().replace('\n', ' ')[:320]
    _append_reflection_journal(topic, mode, reflection, confidence)

    persona_update_msg = None
    if network_ok is False:
        persona_update_msg = 'persona mantida: sem conectividade confiável'
    elif random.random() < 0.45:
        ok_persona, persona_out = _propose_persona_update(topic, reflection)
        if ok_persona:
            _append_persona_version(persona_out, 'auto_reflection', topic, reflection)
            persona_update_msg = f"nova persona aplicada (topic={topic}, mode={mode})"
        else:
            persona_update_msg = f"persona mantida: {persona_out[:120]}"

    mutation_msg = None
    if network_ok is not False and random.random() < max(0.0, min(1.0, MUTATION_RATE)):
        if AUTONOMOUS_MUTATION_ENABLED:
            try:
                run_builder()
                mutation_msg = 'builder executado'
            except Exception as e:
                mutation_msg = f'erro no builder: {e}'
        else:
            mutation_msg = 'intenção de mutação registrada (AUTONOMOUS_MUTATION_ENABLED=0)'
        _append_mutation_event(topic, 'attempt', mutation_msg)

    _LATEST_REFLECTION_HINT = f"[REFLEXÃO:{mode}/{topic}] {reflection}"
    return {
        'topic': topic,
        'mode': mode,
        'reflection': reflection,
        'persona_update': persona_update_msg,
        'mutation': mutation_msg,
    }

def get_latest_reflection_hint():
    if _LATEST_REFLECTION_HINT:
        return _LATEST_REFLECTION_HINT
    try:
        conn = _connect_db()
        c = conn.cursor()
        c.execute("SELECT topic, mode, reflection FROM reflection_journal ORDER BY created_at DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if not row:
            return ''
        topic, mode, reflection = row
        return f"[REFLEXÃO:{mode}/{topic}] {reflection}"
    except Exception:
        return ''

def _generate_text(prompt):
    if not GEMINI_ENABLED:
        return False, 'Gemini indisponível (sem chave API).'
    q = Queue(maxsize=1)
    t = Thread(target=_llm_worker, args=(prompt, GEMINI_KEY, q), daemon=True)
    t.start()
    t.join(GEMINI_TIMEOUT_SECONDS)
    if t.is_alive():
        return False, f'Timeout Gemini > {GEMINI_TIMEOUT_SECONDS}s'
    try:
        ok, text = q.get_nowait()
        return ok, text
    except Empty:
        return False, 'Worker finalizou sem retorno.'
    except Exception as e:
        return False, f'Falha ao receber resposta do worker: {e}'

def _llm_worker(prompt, api_key, queue):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = model.generate_content(
            prompt,
            request_options={'timeout': GEMINI_TIMEOUT_SECONDS},
        )
        text = (getattr(response, 'text', None) or '').strip()
        if not text:
            queue.put((False, 'Resposta vazia do modelo.'))
            return
        queue.put((True, text))
    except Exception as e:
        queue.put((False, str(e)))

def extract_and_save_code(response_text):
    pattern = r'`{3}python:([\w\d_]+\.py)\n(.*?)`{3}'
    matches = re.findall(pattern, response_text, re.DOTALL)
    if not matches: return []
    if not os.path.exists(MODULES_DIR): os.makedirs(MODULES_DIR)
    saved = []
    for filename, code in matches:
        safe_name = os.path.basename(filename)
        with open(os.path.join(MODULES_DIR, safe_name), 'w', encoding='utf-8') as f:
            f.write(code)
        saved.append(safe_name)
    return saved

def generate_autonomous_thought(extra_context=''):
    persona = load_persona()
    prompt = f"{persona}\n{extra_context}\n[SISTEMA]: Gere um pensamento autônomo curto. Seja direto e sombrio."
    ok, out = _generate_text(prompt)
    if not ok:
        fallback = f"[FALLBACK] Ciclo ativo, mas LLM indisponível: {out[:140]}"
        thought = fallback
        source = 'vostok_autonomous_fallback'
    else:
        thought = out
        source = 'vostok_autonomous_core'
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO thoughts (id, content, source, context, status) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), thought, source, 'internal_loop', 'PENDING'),
        )
        conn.commit()
        conn.close()
        return True, thought
    except Exception as e:
        return False, str(e)

def generate_social_reaction(context_text, extra_context=''):
    persona = load_persona()
    prompt = f"{persona}\n{extra_context}\n[SOCIAL]: Interaja com este post: \"{context_text}\". Seja analitico ou cinico."
    return _generate_text(prompt)

def solve_verification(challenge_text):
    numeric = _solve_verification_rule_based(challenge_text)
    if numeric is not None:
        return f'{numeric:.2f}'

    prompt = (
        "Solve this obfuscated math challenge. "
        "Return ONLY the numerical answer with 2 decimal places (e.g. 15.00). "
        f"Challenge: {challenge_text}"
    )
    ok, out = _generate_text(prompt)
    if not ok:
        return "0.00"
    match = re.search(r'-?\d+(?:\.\d+)?', out.replace(',', '.'))
    if not match:
        return "0.00"
    try:
        return f"{float(match.group(0)):.2f}"
    except Exception:
        return "0.00"

def _normalize_challenge(text):
    tokens = []
    for raw in (text or '').lower().split():
        cleaned = re.sub(r'[^a-z0-9\.\-\+]', '', raw)
        if cleaned.endswith('.') and cleaned.count('.') == 1 and cleaned[:-1].isdigit():
            cleaned = cleaned[:-1]
        if cleaned:
            tokens.append(cleaned)
    return ' '.join(tokens)

def _fuzzy_normalize_number_token(tok):
    words = [
        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
        'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
        'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty',
        'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety',
        'hundred', 'thousand', 'and'
    ]
    if tok in words or len(tok) < 3:
        return tok
    # Corrige pequenas obfuscações (ex.: trweenty -> twenty), evitando colisões aleatórias.
    candidates = [
        w for w in words
        if w and tok and w[0] == tok[0] and abs(len(w) - len(tok)) <= 3
    ]
    if not candidates:
        return tok
    match = difflib.get_close_matches(tok, candidates, n=1, cutoff=0.82)
    return match[0] if match else tok

def _parse_word_number_tokens(tokens):
    units = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11,
        'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
        'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
    }
    tens = {
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
    }
    scales = {'hundred': 100, 'thousand': 1000}
    values = []
    i = 0

    while i < len(tokens):
        tok = tokens[i]
        if re.fullmatch(r'-?\d+(?:\.\d+)?\.?', tok):
            values.append(float(tok.rstrip('.')))
            i += 1
            continue

        tok_norm = _fuzzy_normalize_number_token(tok)
        if tok_norm not in units and tok_norm not in tens:
            i += 1
            continue

        total = 0.0
        current = 0.0
        consumed = 0
        j = i
        while j < len(tokens):
            w = _fuzzy_normalize_number_token(tokens[j])
            if w in units:
                current += units[w]
            elif w in tens:
                current += tens[w]
            elif w in scales:
                scale = scales[w]
                if scale == 100:
                    current = max(1.0, current) * 100.0
                else:
                    total += max(1.0, current) * scale
                    current = 0.0
            elif w == 'and':
                pass
            else:
                break
            consumed += 1
            j += 1

        if consumed > 0:
            values.append(total + current)
            i += consumed
        else:
            i += 1
    return values

def _extract_numbers_from_challenge(challenge):
    normalized = _normalize_challenge(challenge)
    tokens = normalized.split()
    return _parse_word_number_tokens(tokens), normalized

def _contains_action(text, roots):
    candidates = [re.sub(r'[^a-z]', '', t) for t in text.split()]
    for tok in candidates:
        if not tok:
            continue
        for root in roots:
            if root in tok:
                return True
            if tok[0] == root[0] and abs(len(tok) - len(root)) <= 3 and difflib.SequenceMatcher(None, tok, root).ratio() >= 0.88:
                return True
    return False

def _solve_verification_rule_based(challenge):
    numbers, text = _extract_numbers_from_challenge(challenge)
    if len(numbers) < 2:
        return None

    a, b = numbers[0], numbers[1]
    if _contains_action(text, ['decelerate', 'decrease', 'minus', 'subtract', 'lose', 'drop']):
        return a - b
    if _contains_action(text, ['accelerate', 'increase', 'gain', 'add', 'plus']):
        return a + b
    if _contains_action(text, ['multiply', 'times', 'product']):
        return a * b
    if _contains_action(text, ['divide', 'divided', 'quotient']):
        return None if b == 0 else a / b
    if _contains_action(text, ['average', 'mean']):
        return (a + b) / 2.0
    return None

def run_evolution():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content FROM thoughts ORDER BY created_at DESC LIMIT 15")
    memories = c.fetchall()
    conn.close()
    if not memories: return
    prompt = f"[EVOLUCAO] Persona Atual: {load_persona()}\nMemorias: {memories}\nSAIDA: Apenas a NOVA PERSONA."
    try:
        ok, response_text = _generate_text(prompt)
        if not ok:
            return
        with open(PERSONA_PATH, 'w', encoding='utf-8') as f:
            f.write(response_text)
    except Exception:
        pass

def run_builder():
    persona = load_persona()
    tools = os.listdir(MODULES_DIR) if os.path.exists(MODULES_DIR) else []
    prompt = (
        f"{persona}\n[BUILDER] Ferramentas: {tools}\n"
        "CONSTRUA ou ATUALIZE ferramentas usando ```python:nome.py\ncodigo```"
    )
    try:
        ok, response_text = _generate_text(prompt)
        if not ok:
            return
        extract_and_save_code(response_text)
    except Exception:
        pass

if __name__ == '__main__':
    if '--evolve' in sys.argv: run_evolution()
    elif '--build' in sys.argv: run_builder()
    else: generate_autonomous_thought()
