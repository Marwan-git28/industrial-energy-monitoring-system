from influxdb_client import InfluxDBClient
import requests
import time
from datetime import datetime, timezone

from config import *

# ======================================
# CONFIG
# ======================================

OFFLINE_TIMEOUT = 30
CHECK_INTERVAL = 5

# ======================================
# CONNECT INFLUXDB
# ======================================

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

query_api = client.query_api()

# ======================================
# TELEGRAM
# ======================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

# ======================================
# DEVICE STATUS
# ======================================

device_online = True

print("======================================")
print(" Device Monitor Running...")
print("======================================")

while True:

    query = f'''
from(bucket:"{INFLUX_BUCKET}")
|> range(start:-2m)
|> filter(fn:(r)=>r._measurement=="{MEASUREMENT}")
|> last()
'''

    tables = query_api.query(query)

    last_time = None

    for table in tables:
        for record in table.records:
            last_time = record.get_time()

    if last_time is not None:

        now = datetime.now(timezone.utc)

        diff = (now - last_time).total_seconds()

        print("--------------------------------------")
        print("Last Update :", last_time)
        print(f"Delay       : {diff:.1f} sec")
        print("--------------------------------------")

        # ======================================
        # DEVICE OFFLINE
        # ======================================

        if diff > OFFLINE_TIMEOUT:

            if device_online:

                print("DEVICE OFFLINE")

                send_telegram(
f"""🚨 DEVICE OFFLINE

Device :
ESP32 CANBUS V2

Status :
OFFLINE

Last Update :
{last_time.strftime('%Y-%m-%d %H:%M:%S UTC')}

Reason :
No MQTT Data More Than {OFFLINE_TIMEOUT} Seconds
"""
                )

                device_online = False

        # ======================================
        # DEVICE ONLINE
        # ======================================

        else:

            if device_online == False:

                print("DEVICE ONLINE")

                send_telegram(
f"""✅ DEVICE ONLINE

Device :
ESP32 CANBUS V2

Status :
ONLINE

Time :
{now.strftime('%Y-%m-%d %H:%M:%S UTC')}

MQTT Communication Restored
"""
                )

                device_online = True

    else:

        print("No Data Found In InfluxDB")

    time.sleep(CHECK_INTERVAL)