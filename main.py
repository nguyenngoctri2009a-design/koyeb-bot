from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running 24/7!"

def run_bot():
    while True:
        print("Bot still alive...")
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8000)
