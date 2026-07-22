import requests

# ==========================================
# TELEGRAM CONFIG
# ==========================================

BOT_TOKEN = "8840304904:AAG3-mpZ29d3jwYtozjFVtqaR01_AlWPlxU"

CHAT_ID = "8837184357"

# ==========================================
# MESSAGE
# ==========================================

message = """
🚜 CANBUS V2

✅ Telegram Test Berhasil

RPM  : 1500 RPM
TEMP : 82 °C
FUEL : 75 %

Python → Telegram
"""

# ==========================================
# SEND
# ==========================================

url = f"https://api.telegram.org/bot8840304904:AAG3-mpZ29d3jwYtozjFVtqaR01_AlWPlxU/sendMessage"

data = {
    
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, data=data)

print("Status Code :", response.status_code)
print(response.text)

if response.status_code == 200:
    print()
    print("=================================")
    print("TELEGRAM SUCCESS")
    print("=================================")
else:
    print()
    print("=================================")
    print("FAILED")
    print("=================================")