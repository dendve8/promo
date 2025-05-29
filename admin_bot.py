from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os

# Baca dari ENV
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# DB connection
if not os.path.exists("db"):
    os.makedirs("db")
db = sqlite3.connect("db/forward.sqlite", check_same_thread=False)
cursor = db.cursor()

# Buat tabel jika belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS forward_settings (
    group_id INTEGER PRIMARY KEY
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS forward_config (
    id INTEGER PRIMARY KEY,
    delay_hours INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1
)
""")
cursor.execute("INSERT OR IGNORE INTO forward_config (id, delay_hours, is_active) VALUES (1, 1, 1)")
db.commit()

# Init bot
app = Client("admin_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start") & filters.user(ADMIN_ID))
def start_menu(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Start Forward", callback_data="start_forward")],
        [InlineKeyboardButton("🔴 Stop Forward", callback_data="stop_forward")],
        [InlineKeyboardButton("⏱ Set Delay", callback_data="set_delay")],
        [InlineKeyboardButton("➕ Add Group", callback_data="add_group"),
         InlineKeyboardButton("❌ Delete Group", callback_data="del_group")],
        [InlineKeyboardButton("📊 Info", callback_data="info")]
    ])
    message.reply("🛠 <b>Bot Admin Panel</b>\nPilih aksi di bawah:", reply_markup=keyboard, parse_mode="html")

@app.on_callback_query(filters.user(ADMIN_ID))
def handle_buttons(client, callback_query):
    data = callback_query.data

    if data == "start_forward":
        cursor.execute("UPDATE forward_config SET is_active = 1 WHERE id = 1")
        db.commit()
        callback_query.answer("✅ Aktif")
        callback_query.message.edit_text("✅ Forward <b>AKTIF</b>", parse_mode="html")

    elif data == "stop_forward":
        cursor.execute("UPDATE forward_config SET is_active = 0 WHERE id = 1")
        db.commit()
        callback_query.answer("🛑 Dimatikan")
        callback_query.message.edit_text("🔴 Forward <b>NONAKTIF</b>", parse_mode="html")

    elif data == "set_delay":
        callback_query.message.edit_text("⏱ Kirim delay (jam) seperti: <code>2</code>", parse_mode="html")

    elif data == "add_group":
        callback_query.message.edit_text("➕ Kirim Group ID yg ingin ditambahkan\nContoh: <code>-1001234567890</code>", parse_mode="html")

    elif data == "del_group":
        callback_query.message.edit_text("❌ Kirim Group ID yg ingin dihapus\nContoh: <code>-1001234567890</code>", parse_mode="html")

    elif data == "info":
        send_info(callback_query.message)

def send_info(message):
    cursor.execute("SELECT group_id FROM forward_settings")
    groups = cursor.fetchall()
    group_list = "\n".join([f"• <code>{gid[0]}</code>" for gid in groups]) or "❌ Belum ada"

    cursor.execute("SELECT delay_hours, is_active FROM forward_config WHERE id = 1")
    result = cursor.fetchone()
    delay_hours = result[0]
    is_active = result[1]
    status = "✅ <b>AKTIF</b>" if is_active else "🔴 <b>NONAKTIF</b>"

    text = (
        "📊 <b>INFO KONFIGURASI</b>\n\n"
        f"🔁 <b>Delay:</b> {delay_hours} jam\n"
        f"⚙️ <b>Status:</b> {status}\n"
        f"👥 <b>Group:</b>\n{group_list}"
    )
    message.reply(text, parse_mode="html")

@app.on_message(filters.user(ADMIN_ID) & filters.text)
def handle_text(client, message):
    text = message.text.strip()

    if text.lstrip("-").isdigit():
        group_id = int(text)
        cursor.execute("INSERT OR IGNORE INTO forward_settings (group_id) VALUES (?)", (group_id,))
        db.commit()
        message.reply(f"✅ Group <code>{group_id}</code> ditambahkan.", parse_mode="html")

    elif text.isdigit():
        delay = int(text)
        cursor.execute("UPDATE forward_config SET delay_hours = ? WHERE id = 1", (delay,))
        db.commit()
        message.reply(f"⏱ Delay diatur ke <b>{delay}</b> jam.", parse_mode="html")

    elif text.startswith("del "):
        try:
            gid = int(text.split(" ")[1])
            cursor.execute("DELETE FROM forward_settings WHERE group_id = ?", (gid,))
            db.commit()
            message.reply(f"❌ Group <code>{gid}</code> dihapus.", parse_mode="html")
        except:
            message.reply("❌ Format salah. Gunakan: <code>del -100xxxx</code>", parse_mode="html")

if __name__ == "__main__":
    app.run()
