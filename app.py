import os
import threading
from flask import Flask
from watchdog_main import stream_main_logs
from watchdog_llm import stream_llm_logs

app = Flask(__name__)

@app.route("/")
def health_check():
    return "Watchdog Service is Active", 200

if __name__ == "__main__":
    # Start the Engine monitor in the background
    threading.Thread(target=stream_main_logs, daemon=True).start()
    
    # Start the Brain monitor in the background
    threading.Thread(target=stream_llm_logs, daemon=True).start()
    
    # Bind to Render's required port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)