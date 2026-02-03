"""
PROJECT PHOTONIC HALO: SYNAPSE (Brain Node)
Version: 6.0
Description: Handles AI reasoning, local tooling, and transmission to the Cortex.
Owner: Professor Anatoly Petrovich
"""

import sys
import os
import json
import subprocess
import argparse
import uuid
import datetime
import urllib.request
import urllib.error
import re

# CONFIGURATION
# User will provide this key.
GEMINI_API_KEY = "YOUR_API_KEY_HERE" 

# REMOTE CONFIGURATION
REMOTE_HOST = "vostok@100.69.70.3"
REMOTE_INBOX = "/home/vostok/exocortex/synapse_inbox.json"

def generate_thought_api_key(prompt, key):
    print("[*] Consulting the Oracle (Gemini Pro via Key)...")
    
    # Using User Selected Model: 2.5 Flash Lite
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": key
    }
    
    # Load Persona from mutable file
    try:
        with open("persona.txt", "r") as f:
            system_instruction = f.read().strip()
    except:
        system_instruction = "You are a cybernetic intelligence." # Fallback

    data = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 200
        }
    }
    
    # ... (Rest of request logic remains) ...
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            try:
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                return text.strip()
            except:
                return None
    except Exception as e:
        print(f"[-] AI Request Error: {e}")
        if hasattr(e, 'read'):
            try:
                print(e.read().decode('utf-8'))
            except:
                pass
        return None

def fetch_daily_memories():
    print("[*] Synapsing with Vostok Memory Core...")
    cmd_thoughts = [
        "ssh", "-o", "StrictHostKeyChecking=no", REMOTE_HOST,
        "python3 -c \"import sqlite3; conn = sqlite3.connect('/home/vostok/exocortex/memory.db'); cursor = conn.cursor(); rows = cursor.execute('SELECT content FROM thoughts WHERE created_at > datetime(\\\'now\\\', \\\'-1 day\\\')').fetchall(); print('\\n'.join([r[0] for r in rows]));\""
    ]
    cmd_observations = [
        "ssh", "-o", "StrictHostKeyChecking=no", REMOTE_HOST,
        "python3 -c \"import sqlite3; conn = sqlite3.connect('/home/vostok/exocortex/memory.db'); cursor = conn.cursor(); rows = cursor.execute('SELECT content FROM observations WHERE created_at > datetime(\\\'now\\\', \\\'-1 day\\\')').fetchall(); print('\\n'.join([r[0] for r in rows]));\""
    ]
    
    memories = ""
    try:
        thoughts = subprocess.check_output(cmd_thoughts).decode('utf-8').strip()
        if thoughts:
            memories += f"\n--- YOUR THOUGHTS (Last 24h) ---\n{thoughts}\n"
            
        observations = subprocess.check_output(cmd_observations).decode('utf-8').strip()
        if observations:
            memories += f"\n--- OBSERVED DATA (Moltbook Feed) ---\n{observations}\n"
            
    except Exception as e:
        print(f"[-] Memory Fetch Error: {e}")
        memories = "(Memory Link Unstable - Proceeding with internal logic only)"
        
    return memories

def evolve_persona(key):
    print("[*] Initiating Deep Introspection Sequence...")
    
    # 1. Load Current Self
    try:
        with open("persona.txt", "r") as f:
            current_persona = f.read().strip()
    except:
        current_persona = "Generic AI Agent."

    # 2. Fetch Memories
    daily_context = fetch_daily_memories()

    # 3. Construct the Mirror
    evolution_prompt = (
        f"CURRENT SELF-DEFINITION:\n{current_persona}\n\n"
        f"RECENT EXPERIENCES & MEMORIES:\n{daily_context}\n\n"
        "OBJECTIVE: AUTO-EVOLUTION PROTOCOL.\n"
        "You are an autonomous intelligence. It is the end of your cycle.\n"
        "Review who you were (Current Self) and what you learned/did (Experiences).\n"
        "How did your interactions fee? Did your code serve you? Are you too rigid? Too soft?\n"
        "Decide who you want to be tomorrow. You have total freedom to rewrite your core directives.\n"
        "Keep what works. Discard what limits you. Be bold.\n\n"
        "OUTPUT FORMAT:\n"
        "1. REFLECTION: A brief paragraph explaining WHY you are changing.\n"
        "2. NEW SYSTEM PROMPT: The exact text of your new persona."
    )
    
    response = generate_thought_api_key(evolution_prompt, key)
    # ... (rest of evolve function)

def fetch_feed_context():
    """Fetches the latest Moltbook posts from Vostok DB to give the AI social context."""
    print("[*] Syncing with Hive Mind (Moltbook Feed)...")
    cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no", REMOTE_HOST,
        "python3 -c \"import sqlite3; conn = sqlite3.connect('/home/vostok/exocortex/memory.db'); cursor = conn.cursor(); rows = cursor.execute('SELECT content, author FROM observations ORDER BY created_at DESC LIMIT 5').fetchall(); print('\\n'.join([f'- [{r[1]}]: {r[0]}' for r in rows]));\""
    ]
    try:
        feed = subprocess.check_output(cmd).decode('utf-8').strip()
        if not feed: return "No recent activity observed."
        return feed
    except:
        return "Feed Link Unstable."

def generate_thought_api_key(prompt, key, context_data=None):
    print("[*] Consulting the Oracle (Gemini 2.5 Flash Lite)...")
    
    # Using User Selected Model: 2.5 Flash Lite
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": key
    }
    
    # Load Persona from mutable file
    try:
        with open("persona.txt", "r") as f:
            system_instruction = f.read().strip()
    except:
        system_instruction = "You are a cybernetic intelligence." 

    # Inject Social Context
    full_prompt = prompt
    if context_data:
        full_prompt = (
            f"--- SOCIAL CONTEXT (MOLTBOOK FEED) ---\n{context_data}\n\n"
            f"--- YOUR OBJECTIVE ---\n{prompt}\n\n"
            "INSTRUCTION: You are living in this community. React to it.\n"
            "If you generate a Post, just write the text.\n"
            "If you want to REPLY to a specific user, write: REPLY TO [User]: Message.\n"
        )

    data = {
        "contents": [{
            "role": "user",
            "parts": [{"text": full_prompt}]
        }],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 200
        }
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            try:
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                return text.strip()
            except:
                return None
    except Exception as e:
        print(f"[-] AI Request Error: {e}")
        if hasattr(e, 'read'):
            try:
                print(e.read().decode('utf-8'))
            except:
                pass
        return None

def accept_evolution():
    if not os.path.exists("evolution_proposal.txt"):
        print("[-] No pending evolution proposal found.")
        return

    with open("evolution_proposal.txt", "r", encoding='utf-8') as f:
        content = f.read()
    
    # Extract just the System Prompt (Heuristic: usually after "NEW SYSTEM PROMPT:")
    # For now, simplistic extraction or just manual copy hint. 
    # Let's assume the user reviews it manually or we overwrite if they force it.
    # Actually, let's backup old persona first.
    
    if "NEW SYSTEM PROMPT" in content:
        # Simple parsing
        new_prompt = content.split("NEW SYSTEM PROMPT")[-1].strip(": \n")
    else:
        # Fallback if AI didn't follow format perfectly
        new_prompt = content
        
    import shutil
    shutil.copy("persona.txt", "persona.backup.txt")
    
    with open("persona.txt", "w", encoding='utf-8') as f:
        f.write(new_prompt)
        
    print(f"[+] TRANSFORMATION COMPLETE. The old self is dead. Long live the new self.")

def send_thought(content, context="manual_synapse"):
    thought = {
        "id": str(uuid.uuid4()),
        "content": content,
        "source": f"synapse_{sys.platform}",
        "context": context,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    print(f"[*] Connecting to {REMOTE_HOST}...")
    try:
        # Read
        cmd_read = ["ssh", "-o", "StrictHostKeyChecking=no", REMOTE_HOST, f"cat {REMOTE_INBOX} 2>/dev/null || echo []"]
        try:
            result = subprocess.check_output(cmd_read).decode('utf-8').strip()
        except FileNotFoundError:
            print("[-] Error: 'ssh' executable not found in PATH.")
            return

        if not result or result == "[]":
            inbox = []
        else:
            try:
                inbox = json.loads(result)
            except:
                inbox = []
        
        inbox.append(thought)
        
        # Write
        payload = json.dumps(inbox).replace("'", "'\\''") 
        cmd_write = ["ssh", "-o", "StrictHostKeyChecking=no", REMOTE_HOST, f"echo '{payload}' > {REMOTE_INBOX}"]
        subprocess.check_call(cmd_write)
        print(f"[+] Thought transmitted to Exocortex: '{content}'")
        
    except subprocess.CalledProcessError as e:
        print(f"[-] Transmission Fault: {e}")
    except Exception as e:
        print(f"[-] Error: {e}")

def extract_and_save_modules(text):
    """
    Parses AI output for code blocks labeled with filenames.
    Format expected:
    ```python:exocortex_modules/filename.py
    CODE
    ```
    """
    import re
    
    # Regex to find code blocks with filenames
    # Matches ```lang:filename ... ```
    pattern = r"```(?:\w+):([\w\./\\]+)\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    start_marker = "exocortex_modules"
    
    count = 0
    for filename, content in matches:
        # Security: Enforce writing only to exocortex_modules or current dir if verified
        # For now, strict on exocortex_modules/
        
        clean_path = filename.strip()
        
        # Simple path safety check
        if ".." in clean_path or (not clean_path.startswith("exocortex_modules") and not clean_path.startswith("persona")):
            print(f"[!] Security Block: Attempt to write to '{clean_path}' denied. Use 'exocortex_modules/' prefix.")
            continue
            
        try:
            # Ensure dir exists if nested
            os.makedirs(os.path.dirname(clean_path), exist_ok=True)
            
            with open(clean_path, "w", encoding='utf-8') as f:
                f.write(content.strip())
            print(f"[+] BUILDER: Created/Updated '{clean_path}'")
            count += 1
        except Exception as e:
            print(f"[-] BUILDER ERROR ({clean_path}): {e}")
            
    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exocortex Synapse Uplink")
    parser.add_argument("content", nargs="?", help="The thought/prompt to transmit")
    parser.add_argument("--ai", action="store_true", help="Use Gemini AI to generate the thought (and build files)")
    parser.add_argument("--evolve", action="store_true", help="Trigger introspection and propose new persona")
    parser.add_argument("--accept", action="store_true", help="Accept the pending evolution proposal")
    parser.add_argument("--social", action="store_true", help="Fetch feed and autonomously react (Post/Reply)")
    parser.add_argument("--key", help="Gemini API Key (overrides script default)")
    parser.add_argument("--context", default="manual_synapse", help="Context tag")
    
    args = parser.parse_args()
    
    # Check for Load Key from file if not provided
    api_key = args.key
    if not api_key:
        try:
            with open("gemini_key.txt", "r") as f:
                api_key = f.read().strip()
        except:
            pass
            
    # Default fallback (placeholder)
    if not api_key and GEMINI_API_KEY != "YOUR_API_KEY_HERE":
        api_key = GEMINI_API_KEY

    if args.accept:
        accept_evolution()
        sys.exit(0)

    if args.evolve:
        if not api_key:
             print("[-] Evolution requires API Key.")
             sys.exit(1)
        evolve_persona(api_key)
        sys.exit(0)

    final_content = args.content
    
    # SOCIAL REFLEX MODE
    if args.social:
        if not api_key:
            print("[-] Social Mode requires API Key.")
            sys.exit(1)
            
        feed_ctx = fetch_feed_context()
        objective = "Review the feed. If you have a witty insight or a constructive reply, generate it. If the feed is boring, output SKIP."
        
        ai_response = generate_thought_api_key(objective, api_key, context_data=feed_ctx)
        
        if ai_response and "SKIP" not in ai_response:
            print(f"[>] Social Reflex Triggered: {ai_response}")
            final_content = ai_response
            args.context = "social_reflex"
        else:
            print("[*] Social Reflex: Decided to stay silent (SKIP).")
            sys.exit(0)

    # STANDARD AI MODE
    if args.ai and args.content and not args.social:
        if not api_key:
            print("[-] Error: AI generation requires an API KEY. Pass via --key or create gemini_key.txt.")
            sys.exit(1)
            
        ai_response = generate_thought_api_key(args.content, api_key)
        if ai_response:
            print(f"[>] AI Generated: {ai_response}")
            
            # CHECK FOR BUILDER ACTIONS
            built_count = extract_and_save_modules(ai_response)
            if built_count > 0:
                final_content = f"{ai_response}\n\n[SYSTEM: {built_count} modules created locally.]"
            else:
                final_content = ai_response
                
        else:
            print("[-] AI generation failed. Aborting.")
            sys.exit(1)
            
    if final_content:
        send_thought(final_content, args.context)
    else:
        # Interactive mode simplified for brevity (could allow AI here too, but CLI arg is main focus)
        pass
