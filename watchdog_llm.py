import requests
import time
import os
from collections import deque # <--- Imports the memory array

SPACE_ID = "sudoboneman/PSI-09-llm"
HF_TOKEN = os.getenv("HF_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_LLM")

# Create a memory bank that holds the last 2000 logs. 
# Using a deque with a maxlen prevents your Render server from running out of RAM.
seen_logs = deque(maxlen=2000)

def stream_llm_logs():
    url = f"https://huggingface.co/api/spaces/{SPACE_ID}/logs/run"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    print(f"Started monitoring {SPACE_ID}...")

    try:
        requests.post(WEBHOOK_URL, json={"content": f"**Watchdog successfully booted and attached to {SPACE_ID}**"})
        print("Startup ping sent to Discord.")
    except Exception as e:
        print(f"CRITICAL: Could not send startup ping to Discord: {e}")

    while True:
        try:
            # Bumped the timeout to 300 (5 minutes) so it disconnects less frequently
            with requests.get(url, headers=headers, stream=True, timeout=300) as response:

                if response.status_code != 200:
                    print(f"Hugging Face rejected connection! HTTP {response.status_code}: {response.text}")
                    time.sleep(10)
                    continue

                for line in response.iter_lines():
                    if line:
                        raw_line = line.decode('utf-8')
                        
                        # --- THE DEDUPLICATOR ---
                        if raw_line in seen_logs:
                            continue # We already sent this to Discord, silently skip it.
                            
                        seen_logs.append(raw_line) # Add it to memory so we don't send it again later.
                        # ------------------------

                        payload = {"content": f"```json\n{raw_line}\n```"}
                        
                        post_response = requests.post(WEBHOOK_URL, json=payload)
                        
                        if post_response.status_code == 429:
                            print("⚠️ Discord Rate Limit hit! Slowing down...")
                            time.sleep(2) 
                                
        except Exception as e:
            print(f"CORTEX stream disconnected: {e}. Retrying in 10s...")
            time.sleep(10)