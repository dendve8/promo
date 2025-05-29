from pyrogram import Client
import time
import os
import sys
import sqlite3
from datetime import datetime

# Baca dari environment
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Buat folder db jika belum ada
if not os.path.exists("db"):
    os.makedirs("db")

# Connect ke database
forward_db = sqlite3.connect("db/forward.sqlite", check_same_thread=False)
forward_cursor = forward_db.cursor()

# Pyrogram Client (pakai session user)
app = Client("promo_session", api_id=api_id, api_hash=api_hash)

def get_forward_settings():
    try:
        forward_cursor.execute("SELECT is_active, delay_hours FROM forward_config WHERE id = 1")
        row = forward_cursor.fetchone()
        if not row or row[0] != 1:
            return [], 3600  # nonaktif atau error
        delay_hours = row[1]
        forward_cursor.execute("SELECT group_id FROM forward_settings")
        group_ids = [r[0] for r in forward_cursor.fetchall()]
        return group_ids, delay_hours * 3600
    except:
        return [], 3600

def forward_to_groups():
    try:
        messages = app.get_chat_history("me", limit=1)
        msg = next(messages, None)
        if not msg or (not msg.text and not msg.media):
            return
        group_ids, _ = get_forward_settings()
        for gid in group_ids:
            try:
                app.forward_messages(gid, "me", msg.id)
            except:
                continue
    except:
        pass

def main():
    try:
        while True:
            _, delay = get_forward_settings()
            forward_to_groups()
            time.sleep(delay)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        forward_db.close()

if __name__ == "__main__":
    with app:
        main()
