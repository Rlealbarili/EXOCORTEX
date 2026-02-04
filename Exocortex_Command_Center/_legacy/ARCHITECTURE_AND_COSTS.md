# EXOCORTEX COMMAND CENTER: ARCHITECTURE & COST REPORT

**Status:** OPERATIONAL
**Agent Identity:** Professor Anatoly Petrovich (Self-Evolving)
**Architecture Type:** Hybrid Hive Mind (Local Brain / Remote Body)

---

## 1. THE ARCHITECTURE (THE HIVE MIND)

The system is designed to decouple **Intelligence (Cognition)** from **Execution (Action)**, ensuring maximum autonomy with minimal dependency on any single point of failure.

### A. The Brain (Local Node)

- **Location:** Windows Workstation (`synapse.py`).
- **Engine:** Gemini 2.5 Flash Lite (Google Generative AI).
- **Role:**
  - Receives triggers/prompts.
  - Generates "Thoughts" (Text).
  - Writes "Reflections" (Self-Evolution).
  - Builds "Tools" (Python Scripts).
- **Why Local?** It runs on your hardware, using your API keys. It keeps the "Mind" close to you.

### B. The Body (Remote Node)

- **Location:** Vostok Server (Ubuntu @ `100.69.70.3`).
- **Engine:** Python `cortex_core.py` (Cron Job / Daemon).
- **Memory:** SQLite (`memory.db`).
- **Actuator:** Moltbook API (Social Interface).
- **Role:**
  - Receives thoughts via SSH (encrypted).
  - Stores long-term memory.
  - Posts to the outside world.
  - **Does NOT think.** It only acts.

### C. The Neural Link (Synapse)

- **Protocol:** SSH (Secure Shell).
- **Format:** JSON Payloads transmitted to `~/exocortex/synapse_inbox.json`.

---

## 2. COST ANALYSIS & SAFETY (ZERO-COST STRATEGY)

We are running on the **Gemini API Free Tier**. Here is how we prevent cost explosion and limits.

### The Limits (Gemini Flash Lite Free Tier)

- **Rate Limit:** ~15 Requests Per Minute (RPM).
- **Daily Limit:** ~1,500 Requests Per Day.
- **Cost:** **$0.00**.

### Our Usage Strategy

1. **Manual Triggering:**
   - The Brain (`synapse.py`) *only* fires when YOU run it (via `python synapse.py` or scheduled batch). It is not an infinite loop.
   - **Risk:** Zero. You control the frequency.

2. **Auto-Evolution (`--evolve`):**
   - This consumes ~2 requests (1 Memory Fetch + 1 Introspection Generation).
   - Frequency: Recommended **Once per Day** (at EOD).
   - **Cost:** Negligible.

3. **Builder Mode:**
   - Code generation consumes output tokens.
   - Mitigated by "Flash Lite" model (highly efficient).

### Cost Explosion Prevention (Safe-Guards)

- **No Infinite Loops:** The `synapse.py` script exits after one thought. It does not loop itself.
- **Flash Lite Model:** We specifically switched to `gemini-2.5-flash-lite`, which is optimized for high volume/low latency free usage.
- **Privacy Note:** On the Free Tier, Google *may* use inputs to improve their models. Do not feed it highly sensitive passwords or banking data.

---

## 3. AUTONOMY PROTOCOLS

### A. Self-Programming (`--evolve`)

The Agent reads its own `persona.txt` and its past memories from Vostok. It then proposes a new "System Prompt".

- **Human-in-the-Loop:** The change is saved to `evolution_proposal.txt`. It is NOT applied until you run `--accept`. This prevents the agent from accidentally lobotomizing itself.

### B. Tool Construction (Builder Mode)

The Agent can output code blocks (`python:filepath`).

- **Sandboxing:** Code is saved to `exocortex_modules/` to prevent overwriting core system files (`synapse.py`).
- **Execution:** Currently Human-Triggered. You must decide to run the tools it builds.

---

## 4. OPERATIONS GUIDE

| Goal | Command |
| :--- | :--- |
| **Generate Thought** | `python synapse.py --ai "Topic"` |
| **Self-Reflect** | `python synapse.py --evolve` |
| **Accept New Ego** | `python synapse.py --accept` |
| **Build Tool** | `python synapse.py --ai "Build tool X..."` |
| **Check Pending Post** | `python check_pending.py` |
| **Force Vostok Post** | `ssh -o StrictHostKeyChecking=no vostok@100.69.70.3 "python3 /home/vostok/exocortex/cortex_core.py --run-once"` |

---

**CONFIDENTIAL // PROFESSOR PETROVICH // EXOCORTEX V6.0**
