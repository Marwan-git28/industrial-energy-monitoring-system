import json
import ssl
import requests
from paho.mqtt import client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from config import *

# =====================================
# INFLUXDB
# =====================================

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# =====================================
# TELEGRAM
# =====================================

gas_alert_sent = False
temp_alert_sent = False

print(">>> SEND TELEGRAM <<<")
def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=data, timeout=10)

        print("Telegram Status :", response.status_code)
        print("Telegram Reply  :", response.text)

    except Exception as e:
        print("Telegram Error :", e)
# =====================================
# MQTT CONNECT
# =====================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    if reason_code == 0:

        print("===================================")
        print(" MQTT Connected")
        print(" Topic :", MQTT_TOPIC)
        print("===================================")

        client.subscribe(MQTT_TOPIC)

    else:

        print("MQTT Failed :", reason_code)


# =====================================
# MQTT MESSAGE
# =====================================

def on_message(client, userdata, msg):

    try:

        payload = json.loads(msg.payload.decode())

        temperature = float(payload["temperature"])
        humidity = float(payload["humidity"])
        gas = int(payload["gas"])

        print("--------------------------------")
        print(f"Temperature : {temperature:.2f} °C")
        print(f"Humidity    : {humidity:.2f} %")
        print(f"Gas         : {gas}")

        point = (
            Point(MEASUREMENT)
            .field("temperature", temperature)
            .field("humidity", humidity)
            .field("gas", gas)
        )

        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )

        print("Data Saved To InfluxDB")
        print("--------------------------------\n")

        global gas_alert_sent
        global temp_alert_sent

        # ============================
        # GAS ALERT
        # ============================

        if gas >= 1000:

            if not gas_alert_sent:

                message = (
                    "🚨 GAS ALERT 🚨\n\n"
                    f"Gas : {gas}\n"
                    f"Temperature : {temperature:.1f} °C\n"
                    f"Humidity : {humidity:.1f} %"
                )

                send_telegram(message)
                gas_alert_sent = True

        else:
            gas_alert_sent = False


        # ============================
        # TEMPERATURE ALERT
        # ============================

        if temperature >= 35:

            if not temp_alert_sent:

                message = (
                    "🌡️ HIGH TEMPERATURE 🌡️\n\n"
                    f"Temperature : {temperature:.1f} °C\n"
                    f"Humidity : {humidity:.1f} %\n"
                    f"Gas : {gas}"
                )

                send_telegram(message)
                temp_alert_sent = True

        else:
            temp_alert_sent = False


    except Exception as e:

        print("Error :", e)

# =====================================
# MQTT CLIENT
# =====================================

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID
)

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_message = on_message

print("Connecting MQTT...")

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)

client.loop_forever()