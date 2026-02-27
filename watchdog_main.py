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

    try:
        requests.post(WEBHOOK_URL, json={"content": f" **Watchdog successfully booted and attached to {SPACE_ID}**"})
        print("Startup ping sent to Discord.")
    except Exception as e:
        print(f"CRITICAL: Could not send startup ping to Discord: {e}")

    while True:
        try:
            with requests.get(url, headers=headers, stream=True, timeout=120) as response:

                if response.status_code != 200:
                    print(f"Hugging Face rejected connection! HTTP {response.status_code}: {response.text}")
                    time.sleep(10)
                    continue

                for line in response.iter_lines():
                    if line:
                        raw_line = line.decode('utf-8')
                        payload = {"content": f"```json\n{raw_line}\n```"}
                        post_response = requests.post(WEBHOOK_URL, json=payload)

                        if post_response.status_code == 429:
                            print("Discord Rate Limit hit. Critical Error Apparent.")
                            time.sleep(2) # Pause briefly so Discord doesn't ban the webhook

        except Exception as e:
            print(f"Engine stream disconnected: {e}. Retrying in 10s...")
            time.sleep(10)