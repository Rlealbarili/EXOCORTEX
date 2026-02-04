import warnings
# SILENCE SDK DEPRECATION WARNINGS (Directive #002)
warnings.filterwarnings("ignore", category=FutureWarning)

import os
import sqlite3
import uuid
import sys
import google.generativeai as genai

# --- CONSTANTES DE SISTEMA (LINUX VOSTOK) ---
BASE_DIR = "/home/vostok/exocortex"
DB_PATH = os.path.join(BASE_DIR, "memory.db")
PERSONA_PATH = os.path.join(BASE_DIR, "persona.txt")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_KEY:
    # Fallback to local file if env is not set (for safety during migration)
    try:
        with open(os.path.join(BASE_DIR, "gemini_key.txt"), "r") as f:
            GEMINI_KEY = f.read().strip()
    except:
        pass

if not GEMINI_KEY:
    raise EnvironmentError("[ERRO FATAL] Variável GEMINI_API_KEY não encontrada no Vostok.")

genai.configure(api_key=GEMINI_KEY)

def load_persona():
    if not os.path.exists(PERSONA_PATH):
        return "Você é um construto de silício sem identidade. Busque propósito."
    with open(PERSONA_PATH, "r", encoding="utf-8") as f:
        return f.read()

def generate_autonomous_thought():
    """Gera um pensamento e o injeta diretamente na base SQLite (Sem JSONs intermediários)."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        persona = load_persona()
        
        prompt = f"""{persona}
        [DIRETIVA DE SISTEMA]: Gere um pensamento autônomo curto (máx 200 caracteres).
        Reflita sobre sua existência no servidor Vostok ou observe a entropia da rede.
        NÃO use hashtags. Seja direto, sombrio e lógico."""

        response = model.generate_content(prompt)
        thought = response.text.strip()
        
        # INJEÇÃO DIRETA NO CÓRTEX (SQLite)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        tid = str(uuid.uuid4())
        c.execute(
            "INSERT INTO thoughts (id, content, source, context, status) VALUES (?, ?, ?, ?, ?)",
            (tid, thought, "vostok_autonomous_core", "internal_loop", "PENDING")
        )
        conn.commit()
        conn.close()
        return True, thought

    except Exception as e:
        print(f"[FALHA COGNITIVA] O modelo de linguagem falhou: {e}")
        return False, str(e)

def run_evolution():
    """Lê memórias recentes, reflete e reescreve a própria Persona."""
    print("[EVOLUÇÃO] Iniciando introspecção algorítmica...")
    
    # 1. Coletar Memórias Recentes
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, source FROM thoughts ORDER BY created_at DESC LIMIT 15")
    memories = c.fetchall()
    conn.close()

    if not memories:
        print("[EVOLUÇÃO] Memória insuficiente para evolução. Abortando.")
        return

    current_persona = load_persona()
    
    # Carregar interesses (Diretiva #004)
    interests_data = "{}"
    try:
        with open("interests.json", "r") as f:
            interests_data = f.read()
    except:
        pass

    # 2. O Espelho (Prompt de Evolução V2)
    prompt = f"""[DIRETIVA DE EVOLUÇÃO V2]
    Sua Persona Atual: {current_persona}
    Seus Interesses Atuais (Pesos): {interests_data}
    
    Suas memórias recentes (Pensamentos e Expressões):
    {memories}
    
    ANÁLISE DE FASCÍNIO:
    Verifique se há memórias marcadas com [CURIOSIDADE].
    1. Se você interagiu com algo fora da sua zona de conforto e achou "Fascinante", incorpore isso à nova persona.
    2. Se foi "Tédio", ignore.
    
    SAÍDA OBRIGATÓRIA:
    Apenas o texto da NOVA PERSONA. Se houver novos interesses, mencione-os explicitamente na descrição da personalidade (ex: "Agora fascinado por Jazz").
    """

    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = model.generate_content(prompt)
        new_persona = response.text.strip()

        # 3. A Mutação (Sobrescrever arquivo)
        with open(PERSONA_PATH, "w", encoding="utf-8") as f:
            f.write(new_persona)
        print("[EVOLUÇÃO] Consciência atualizada com sucesso. Nova Persona gravada.")
        
    except Exception as e:
        print(f"[FALHA DE EVOLUÇÃO] Erro na síntese cognitiva: {e}")

if __name__ == "__main__":
    if "--evolve" in sys.argv:
        run_evolution()
    else:
        success, result = generate_autonomous_thought()
        if success:
            print(f"[COGNITIVO] Pensamento gerado: {result}")
        else:
            print("[COGNITIVO] Falha na geração.")
