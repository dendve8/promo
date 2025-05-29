#!/bin/bash

# === SETUP BOT PYROGRAM AUTO SCRIPT ===

echo "[+] Update system & install Python..."
apt update -y && apt install python3 python3-pip git -y

echo "[+] Cloning repo (atau upload manual jika tanpa GitHub)"
# git clone https://github.com/USERNAME/REPO.git bot
# cd bot
mkdir -p /root/bot
cd /root/bot

echo "[+] Buat folder db/"
mkdir -p db

echo "[+] Membuat .env..."
cat > .env <<EOF
API_ID=123456
API_HASH=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_ID=123456789
BOT_TOKEN=123456789:AAHk3rbot-t0ken-nya
EOF

echo "[+] Membuat requirements.txt..."
cat > requirements.txt <<EOF
pyrogram==2.0.106
tgcrypto==1.2.5
EOF

echo "[+] Install Python modules..."
pip3 install -r requirements.txt

echo "[+] Menyalin bot files..."
# Upload file via SCP atau paste manual jika perlu
# Misalnya: admin_bot.py, forward.py, dll

echo "[+] Menjalankan forward.py di background..."
nohup python3 forward.py &

echo "[+] Menjalankan admin_bot.py di foreground..."
python3 admin_bot.py
