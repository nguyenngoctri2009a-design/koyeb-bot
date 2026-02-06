# -*- coding: utf-8 -*-
import telebot
import requests
import time
import threading
import re
import os
import random
import pyfiglet
from keep_alive import keep_alive  # Gọi server ảo

# --- KHỞI ĐỘNG SERVER GIỮ KẾT NỐI ---
keep_alive()

# --- CẤU HÌNH BOT ---
API_TOKEN = '8200257290:AAGaen1FUtTs5R3smfRkUUQas3qrG_OjAlA'
bot = telebot.TeleBot(API_TOKEN)

# --- DỮ LIỆU GỐC (ĐỌC TỪ FILE TXT) ---
def load_cau_chui():
    try:
        if not os.path.exists('cau_chui.txt'):
            return ["Data loi", "Vui long tao file"], ["Data loi", "cau_chui.txt"]
        
        with open('cau_chui.txt', 'r', encoding='utf-8') as f:
            content = f.read().strip().split('---')
            
        if len(content) >= 2:
            list_1 = [line.strip() for line in content[0].strip().split('\n') if line.strip()]
            list_2 = [line.strip() for line in content[1].strip().split('\n') if line.strip()]
            return list_1, list_2
        else:
            return ["Lỗi file cau_chui.txt"], ["Thiếu dấu --- ngăn cách"]
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return ["Lỗi data"], ["Lỗi data"]

CAU_CHUI_1, CAU_CHUI_2 = load_cau_chui()

# --- CLASS MESSENGER ---
class Messenger:
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_id = self.get_user_id()
        self.fb_dtsg = None
        self.init_params()

    def get_user_id(self):
        try:
            return re.search(r"c_user=(\d+)", self.cookie).group(1)
        except:
            return "Unknown"

    def init_params(self):
        headers = {'Cookie': self.cookie, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            # Dùng mbasic để nhẹ và dễ lấy fb_dtsg hơn
            response = requests.get('https://mbasic.facebook.com', headers=headers, timeout=10)
            match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
            if match:
                self.fb_dtsg = match.group(1)
            else:
                pass # Không in lỗi rác để tránh spam log
        except Exception as e:
            print(f"Lỗi Init {self.user_id}: {e}")

    def send_message(self, recipient_id, message):
        if not self.fb_dtsg: return False
        url = "https://www.facebook.com/messaging/send/"
        data = {
            'fb_dtsg': self.fb_dtsg,
            '__user': self.user_id,
            'body': message,
            'action_type': 'ma-type:user-generated-message',
            'timestamp': int(time.time() * 1000),
            'source': 'source:chat:web',
            'thread_fbid': recipient_id
        }
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        try:
            response = requests.post(url, data=data, headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False

# --- QUẢN LÝ DỮ LIỆU USER ---
user_db = {} 

def get_user_data(uid):
    if uid not in user_db:
        user_db[uid] = {'cookies': [], 'box_id': '', 'delay': 5, 'msgs': [], 'running': False}
    return user_db[uid]

# --- LUỒNG GỬI TIN ---
def send_messages_thread(chat_id, messenger, recipient_id, message_list, delay):
    while user_db.get(chat_id, {}).get('running'):
        try:
            if not message_list: break
            raw_entry = random.choice(message_list)
            parts = [m.strip() for m in raw_entry.split(',') if m.strip()]
            
            for message in parts:
                if not user_db.get(chat_id, {}).get('running'): break
                messenger.send_message(recipient_id, message)
                # In ra log đơn giản để theo dõi trên Koyeb
                print(f"[Run] {messenger.user_id} -> {recipient_id}")
                time.sleep(delay)
        except:
            time.sleep(5)

# --- TELEGRAM HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Đã xóa parse_mode="Markdown" để tránh lỗi bot không chạy
    text = (
        "🔥 BOT SPAM MESSENGER - KOYEB VERSION 🔥\n\n"
        "1. /cookie <list_cookie>\n"
        "2. /id <box_id>\n"
        "3. /delay <seconds>\n"
        "4. /mode <1-6> [nội dung]\n"
        "5. /run (Chạy)\n"
        "6. /stop (Dừng)"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['cookie'])
def set_cookie(message):
    uid = message.chat.id
    raw = message.text.replace('/cookie', '').strip()
    if not raw: return bot.reply_to(message, "❌ Thiếu cookie.")
    cookies = [c.strip() for c in raw.split('\n') if "c_user" in c]
    get_user_data(uid)['cookies'] = cookies
    bot.reply_to(message, f"✅ Đã nhận {len(cookies)} Cookie.")

@bot.message_handler(commands=['id'])
def set_id(message):
    uid = message.chat.id
    bid = message.text.replace('/id', '').strip()
    get_user_data(uid)['box_id'] = bid
    bot.reply_to(message, f"✅ ID Box: {bid}")

@bot.message_handler(commands=['delay'])
def set_delay(message):
    try:
        d = float(message.text.split()[1])
        get_user_data(message.chat.id)['delay'] = d
        bot.reply_to(message, f"✅ Delay: {d}s")
    except: bot.reply_to(message, "❌ Lỗi cú pháp.")

@bot.message_handler(commands=['mode'])
def set_mode(message):
    uid = message.chat.id
    args = message.text.split(maxsplit=2)
    if len(args) < 2: return bot.reply_to(message, "❌ Chọn mode 1-6.")
    
    choice = args[1]
    extra = args[2] if len(args) > 2 else ""
    data = get_user_data(uid)
    
    if choice == '1': data['msgs'] = CAU_CHUI_1
    elif choice == '2': data['msgs'] = CAU_CHUI_2
    elif choice == '3': data['msgs'] = [f"sua di {extra}", f"cay ak {extra}"]
    elif choice == '4': data['msgs'] = [extra]
    elif choice == '5': data['msgs'] = ["Chuc nang file tam khoa tren cloud"]
    elif choice == '6': data['msgs'] = [f"Lag {extra}"]
    
    bot.reply_to(message, f"✅ Đã set Mode {choice}")

@bot.message_handler(commands=['run'])
def run_tool(message):
    uid = message.chat.id
    data = get_user_data(uid)
    if not data['cookies'] or not data['box_id']:
        return bot.reply_to(message, "❌ Chưa nhập Cookie hoặc ID Box.")
    
    if data['running']: return bot.reply_to(message, "⚠️ Đang chạy rồi.")
    
    data['running'] = True
    bot.reply_to(message, "🚀 Bắt đầu spam...")
    
    for ck in data['cookies']:
        m = Messenger(ck)
        if m.user_id:
            t = threading.Thread(target=send_messages_thread, args=(uid, m, data['box_id'], data['msgs'], data['delay']))
            t.daemon = True
            t.start()

@bot.message_handler(commands=['stop'])
def stop_tool(message):
    if message.chat.id in user_db:
        user_db[message.chat.id]['running'] = False
        bot.reply_to(message, "🛑 Đã dừng.")

# --- CHẠY BOT ---
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
