from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot Anh Tri dang chay ngon lanh!"

def run():
    # Chạy trên port 8000 để khớp cấu hình Koyeb
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()
