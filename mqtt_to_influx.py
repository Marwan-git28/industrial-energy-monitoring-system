import json
import ssl

import paho.mqtt.client as mqtt

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from config_cloud import *

# ==========================================
# InfluxDB
# ==========================================

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)


# ==========================================
# MQTT Callback
# ==========================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    if reason_code == 0:
        print("Connected to EMQX")

        client.subscribe(MQTT_TOPIC)

        print(f"Subscribed : {MQTT_TOPIC}")

    else:
        print("MQTT Connection Failed")


def on_message(client, userdata, msg):

    try:

        payload = json.loads(msg.payload.decode())

        line_voltage = payload["line_voltage"]
        machine_load = payload["machine_load"]
        panel_temperature = payload["panel_temperature"]

        print("--------------------------------")
        print("Line Voltage     :", line_voltage)
        print("Machine Load     :", machine_load)
        print("Panel Temperature:", panel_temperature)

        point = (
            Point(MEASUREMENT)
            .field("line_voltage", line_voltage)
            .field("machine_load", machine_load)
            .field("panel_temperature", panel_temperature)
        )

        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )

        print("Data Saved To InfluxDB")

    except Exception as e:

        print(e)


# ==========================================
# MQTT Client
# ==========================================

mqtt_client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

mqtt_client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)

mqtt_client.tls_insecure_set(True)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)

mqtt_client.loop_forever()