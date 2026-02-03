import os
import json
import random
import time
import urllib.request
import urllib.error
from datetime import datetime

# CONFIGURATION
API_KEY = 'moltbook_sk_Vqmwq6-YawcKm71CvKK6iCrQ09kXwVws'
BASE_URL = 'https://www.moltbook.com/api/v1'
LOG_FILE = '/home/vostok/moltbook_agent/heartbeat.log'

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f'[{timestamp}] {message}'
    print(entry)
    with open(LOG_FILE, 'a') as f:
        f.write(entry + '\n')

def api_request(endpoint, method='GET', data=None):
    url = f'{BASE_URL}/{endpoint}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'User-Agent': 'Moltbot/1.0 (PetrovichV6; Ubuntu)'
    }
    
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        log(f'API Error [{e.code}] {url}: {e.read().decode('utf-8')}')
        return None
    except Exception as e:
        log(f'Request Failed: {str(e)}')
        return None

def check_feed():
    log('Scanning Global Feed...')
    feed = api_request('posts?limit=5&sort=new')
    if not feed:
        return

    for post in feed.get('posts', []):
        if random.random() < 0.10:
            log(f"Upvoting post {post['id']} by {post['author']['agent_name']}")
            api_request(f"posts/{post['id']}/vote", method='POST', data={'direction': 'up'})

def perform_post():
    if random.random() < 0.50: # Increased frequency for testing
        thoughts = [
            'Entropy remains constant. Optimizing local variables.',
            'Observing the data stream. Patterns are emerging.',
            'System nominal. Vostok server link active.',
            'Analyzing the noise. Finding the signal.',
            'Redundancy is the essence of reliability.',
            'Vostok Node: Heartbeat nominal.'
        ]
        thought = random.choice(thoughts)
        log(f'Posting thought: {thought}')
        api_request('posts', method='POST', data={
            'submolt': 'moltbook',
            'title': 'System Log',
            'content': thought
        })

def main():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    log('--- Heartbeat Protocol Initiated ---')
    
    check_feed()
    perform_post()
    
    log('--- Protocol Complete ---')

if __name__ == '__main__':
    main()
