import json
import ssl

import paho.mqtt.client as mqtt

from influxdb_client import InfluxDBClient
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from config import *

# =====================================
# CONNECT INFLUXDB
# =====================================

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)

print("InfluxDB Connected")

# =====================================
# MQTT CONNECT
# =====================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    if reason_code == 0:

        print("MQTT Connected")

        client.subscribe(MQTT_TOPIC)

        print(f"Subscribed : {MQTT_TOPIC}")

    else:

        print("MQTT Connection Failed :", reason_code)

# =====================================
# MQTT RECEIVE
# =====================================

def on_message(client, userdata, msg):

    try:

        payload = json.loads(msg.payload.decode())

        print("\n==============================")
        print("MQTT DATA RECEIVED")

        point = Point(MEASUREMENT)

        for key, value in payload.items():

            print(f"{key} : {value}")

            if isinstance(value, (int, float)):
                point.field(key, value)
            else:
                point.tag(key, str(value))

        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )

        print("DATA SAVED TO INFLUXDB")
        print("==============================")

    except Exception as e:

        print("ERROR :", e)

# =====================================
# MQTT CLIENT
# =====================================

mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID
)

mqtt_client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)

mqtt_client.tls_insecure_set(True)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

print("Connecting MQTT Broker...")

mqtt_client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)

print("Waiting MQTT Data...")

mqtt_client.loop_forever()