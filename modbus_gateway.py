# ==========================================
# MODBUS GATEWAY
# Read Modbus RTU
# Save InfluxDB
# Publish MQTT
# ==========================================

import json
import ssl
import time
import requests

from pymodbus.client import ModbusSerialClient

from paho.mqtt import client as mqtt

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from config import *

# ==========================================
# INFLUXDB
# ==========================================

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx_client.write_api(
    write_options=SYNCHRONOUS
)

# ==========================================
# MODBUS
# ==========================================

modbus = ModbusSerialClient(

    port=MODBUS_PORT,
    baudrate=MODBUS_BAUDRATE,

    bytesize=MODBUS_BYTESIZE,
    parity=MODBUS_PARITY,
    stopbits=MODBUS_STOPBITS,

    timeout=MODBUS_TIMEOUT

)

# ==========================================
# MQTT
# ==========================================

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

# ==========================================
# TELEGRAM
# ==========================================

temp_alert = False

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {

        "chat_id": CHAT_ID,
        "text": message

    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=10
        )

        print("Telegram :", response.status_code)

    except Exception as e:

        print("Telegram Error :", e)

# ==========================================
# CONNECT MQTT
# ==========================================

print("Connecting MQTT...")

client.connect(

    MQTT_BROKER,
    MQTT_PORT,
    60

)

client.loop_start()

print("MQTT Connected")

# ==========================================
# CONNECT MODBUS
# ==========================================

print("Connecting Modbus...")

if modbus.connect():

    print("Modbus Connected")

else:

    print("Modbus Failed")
    exit()

print("==============================")
print(" MODBUS GATEWAY READY ")
print("==============================")

# ==========================================
# MAIN LOOP
# ==========================================

while True:

    print("Loop Running")

    try:

        print("Reading Register...")

        rr = modbus.read_holding_registers(
            address=0,
            count=3,
            device_id=MODBUS_SLAVE_ID
        )

        print("Response :", rr)

        if rr.isError():
            print("Read Register Failed")
            time.sleep(1)
            continue

        print("Registers :", rr.registers)

        line_voltage = rr.registers[0]
        machine_load = rr.registers[1]
        panel_temperature = rr.registers[2]

        print("--------------------------------")
        print("line_voltage :", line_voltage)
        print("machine_load :", machine_load)
        print("panel_temperature :", panel_temperature)

        # ==========================================
        # SAVE TO INFLUXDB
        # ==========================================

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

        print("Saved To InfluxDB")

    except Exception as e:
        print("ERROR :", e)
        time.sleep(1)
        continue

        # ==========================================
        # MQTT PUBLISH
        # ==========================================

        payload = {

            "line_voltage": voltage,
            "load_machine": load,
            "panel_temperature": temperature

        }

        client.publish(
            MQTT_TOPIC,
            json.dumps(payload)
        )

        print("MQTT Publish Success")

        # ==========================================
        # TELEGRAM ALERT
        # ==========================================


        if panel_temperature >= 40:

            if not temp_alert:

                message = (
                    "🌡️ HIGH TEMPERATURE 🌡️\n\n"
                    f"Voltage : {line_voltage} V\n"
                    f"Load : {load_machine} W\n"
                    f"Temperature : {panel_temperature} °C"
                )

                send_telegram(message)

                temp_alert = True

        else:

            temp_alert = False

        print("--------------------------------")

        time.sleep(1)

    except KeyboardInterrupt:

        print("Program Stopped")
        break

    except Exception as e:

        print("Error :", e)

        time.sleep(2)

# ==========================================
# CLOSE CONNECTION
# ==========================================

modbus.close()

client.loop_stop()

client.disconnect()

print("Program Closed")
