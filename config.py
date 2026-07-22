# ============================================
# CONFIG PROJECT CANBUS V2
# ============================================

# ==========================
# MQTT EMQX CLOUD
# ==========================

MQTT_BROKER = "bbb5b116.ala.asia-southeast1.emqxsl.com"
MQTT_PORT = 8883

MQTT_USERNAME = "esp32"
MQTT_PASSWORD = "esp32@123"

MQTT_TOPIC = "iot/environment"

CLIENT_ID = "environment_subscriber"


# ==========================
# INFLUXDB
# ==========================

INFLUX_URL = "http://localhost:8086"

INFLUX_TOKEN = "tKBGmQGtQk4H9xGbdbbktaBvzLqU2ae5tu7815zUTzH51OLtAh5kIjueFSdL75QQYcxkzYuPa1Y2tA12fEt5EQ=="

INFLUX_ORG = "IndustrialMonitoring"

INFLUX_BUCKET = "telematics"

MEASUREMENT = "industrial_data"

# ==========================
# TELEGRAM
# ==========================

BOT_TOKEN = "8840304904:AAG3-mpZ29d3jwYtozjFVtqaR01_AlWPlxU"

CHAT_ID = "8837184357"


# ==========================
# GMAIL SMTP
# ==========================

EMAIL_SENDER = "projectesp32.mrwn@gmail.com"

EMAIL_PASSWORD = "ospt vpxm uxaj uwwu"

EMAIL_RECEIVER = "marwan.siputra@gmail.com"
