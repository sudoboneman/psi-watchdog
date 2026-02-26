import requests
import json
import time
import os

SPACE_ID = "sudoboneman/PSI-09-main"
HF_TOKEN = os.getenv("HF_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_MAIN")

def stream_main_logs():
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
                                
                                # Alert on Python crashes or Flask errors
                                if "[ERROR]" in message or "Traceback" in message or "Exception" in message:
                                    payload = {"content": f" **ENGINE ALERT** \n```text\n{message}\n```"}
                                    requests.post(WEBHOOK_URL, json=payload)
                                    
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            print(f"Engine stream disconnected: {e}. Retrying in 10s...")
            time.sleep(10)