import json
import ssl
import paho.mqtt.client as mqtt

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from config import *

# ============================
# InfluxDB
# ============================

influx = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx.write_api(write_options=SYNCHRONOUS)

# ============================
# MQTT CONNECT
# ============================

def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("=================================")
        print("MQTT Connected")
        print("Topic :", MQTT_TOPIC)
        print("=================================")

        client.subscribe(MQTT_TOPIC)

    else:
        print("MQTT Failed :", rc)

# ============================
# MQTT MESSAGE
# ============================

def on_message(client, userdata, msg):

    try:

        data = json.loads(msg.payload.decode())

        voltage = data["voltage"]
        current = data["current"]
        power = data["power"]
        energy = data["energy"]
        frequency = data["frequency"]
        powerfactor = data["powerfactor"]

        print("==============================")
        print("Voltage     :", voltage)
        print("Current     :", current)
        print("Power       :", power)
        print("Energy      :", energy)
        print("Frequency   :", frequency)
        print("PowerFactor :", powerfactor)
        print("==============================")

        point = (
            Point(MEASUREMENT)
            .field("voltage", voltage)
            .field("current", current)
            .field("power", power)
            .field("energy", energy)
            .field("frequency", frequency)
            .field("powerfactor", powerfactor)
        )

        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )

        print("InfluxDB Write OK\n")

    except Exception as e:
        print("ERROR :", e)

# ============================
# MQTT CLIENT
# ============================

client = mqtt.Client(client_id=CLIENT_ID)

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_message = on_message

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)

client.loop_forever()