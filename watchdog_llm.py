import requests
import json
import time
import os

SPACE_ID = "sudoboneman/PSI-09-llm"
HF_TOKEN = os.getenv("HF_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_LLM")

def stream_llm_logs():
    url = f"https://huggingface.co/api/spaces/{SPACE_ID}/logs/run"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    print(f"Started monitoring {SPACE_ID}...")

    while True:
        try:
            with requests.get(url, headers=headers, stream=True, timeout=120) as response:
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith("data: "):
                            try:
                                log_data = json.loads(decoded[6:])
                                message = log_data.get("log", "").strip()
                                
                                # Alert on Model loading failures or Out of Memory errors
                                if "error" in message.lower() or "failed" in message.lower() or "OOM" in message:
                                    payload = {"content": f" **CORTEX ALERT** \n```text\n{message}\n```"}
                                    requests.post(WEBHOOK_URL, json=payload)
                                    
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            print(f"CORTEX stream disconnected: {e}. Retrying in 10s...")
            time.sleep(10)