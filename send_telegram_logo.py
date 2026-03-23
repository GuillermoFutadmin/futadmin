import os
import requests
import psycopg2

TELEGRAM_TOKEN = "8765470114:AAFrXsJcHu4-3N8E5sY00vBg_W6ODNsFSz4"
IMG_PATH = r"C:\Users\Memo\.gemini\antigravity\brain\d1db75f4-2160-4082-b904-b300862b2d58\futadmin_logo_profile_1774217482363.png"

def get_admin_chat_id():
    try:
        conn = psycopg2.connect("postgresql://postgres:Gd012354R1.@localhost:5432/futadmin")
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_id FROM users WHERE rol='admin' AND telegram_id IS NOT NULL LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row: return row[0]
    except Exception as e:
        print("Postgres users error:", e)
        try:
            conn = psycopg2.connect("postgresql://postgres:Gd012354R1.@localhost:5432/futadmin")
            cursor = conn.cursor()
            cursor.execute("SELECT telegram_id FROM usuarios WHERE rol='admin' AND telegram_id IS NOT NULL LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if row: return row[0]
        except Exception as e2:
            print("Postgres usuarios error:", e2)
    return None

chat_id = get_admin_chat_id()

if not chat_id:
    print("Could not find admin chat_id in database. Will ask user for their chat id.")
else:
    print(f"Sending to chat_id: {chat_id}")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(IMG_PATH, 'rb') as f:
        response = requests.post(url, data={'chat_id': chat_id, 'caption': 'FutAdmin Logo'}, files={'photo': f})
        print(response.json())
