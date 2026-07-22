from influxdb_client import InfluxDBClient
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

from config import *

# ===============================
# CONNECT INFLUXDB
# ===============================

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)


query_api = client.query_api()


# ===============================
# FUNCTION QUERY
# ===============================

def get_value(query):

    tables = query_api.query(query)

    for table in tables:
        for record in table.records:
            return record.get_value()

    return None


# ===============================
# RPM MAX
# ===============================

rpm_max = get_value(f'''
from(bucket:"{INFLUX_BUCKET}")
|> range(start:-24h)
|> filter(fn:(r)=>r._measurement=="vehicle_data")
|> filter(fn:(r)=>r._field=="rpm")
|> max()
''')


# ===============================
# RPM AVG
# ===============================

rpm_avg = get_value(f'''
from(bucket:"{INFLUX_BUCKET}")
|> range(start:-24h)
|> filter(fn:(r)=>r._measurement=="vehicle_data")
|> filter(fn:(r)=>r._field=="rpm")
|> mean()
''')


# ===============================
# TEMP MAX
# ===============================

temp_max = get_value(f'''
from(bucket:"{INFLUX_BUCKET}")
|> range(start:-24h)
|> filter(fn:(r)=>r._measurement=="vehicle_data")
|> filter(fn:(r)=>r._field=="temp")
|> max()
''')


# ===============================
# TEMP AVG
# ===============================

temp_avg = get_value(f'''
from(bucket:"{INFLUX_BUCKET}")
|> range(start:-24h)
|> filter(fn:(r)=>r._measurement=="vehicle_data")
|> filter(fn:(r)=>r._field=="temp")
|> mean()
''')


# ===============================
# LAST FUEL
# ===============================

fuel_last = get_value(f'''
from(bucket:"{INFLUX_BUCKET}")
|> range(start:-24h)
|> filter(fn:(r)=>r._measurement=="vehicle_data")
|> filter(fn:(r)=>r._field=="fuel")
|> last()
''')


# ===============================
# EMAIL BODY
# ===============================

today = datetime.now().strftime("%d %B %Y")

body = f"""
======================================
CANBUS V2 DAILY REPORT
======================================

Date :
{today}

RPM
Max : {rpm_max:.0f} RPM
Average : {rpm_avg:.0f} RPM

Temperature
Max : {temp_max:.1f} °C
Average : {temp_avg:.1f} °C

Fuel
Last Value : {fuel_last:.1f} %

Status :
System Running Normal

Generated Automatically
Python + InfluxDB + Gmail SMTP
"""


# ===============================
# SEND EMAIL
# ===============================

msg = MIMEText(body)

msg["Subject"] = "CANBUS V2 Daily Report"

msg["From"] = EMAIL_SENDER

msg["To"] = EMAIL_RECEIVER


server = smtplib.SMTP("smtp.gmail.com",587)

server.starttls()

server.login(
    EMAIL_SENDER,
    EMAIL_PASSWORD
)

server.send_message(msg)

server.quit()

print("EMAIL SENT SUCCESSFULLY")