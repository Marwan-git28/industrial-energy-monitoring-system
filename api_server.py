from flask import Flask, jsonify
from influxdb_client import InfluxDBClient
from config_cloud import *

app = Flask(__name__)

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

query_api = client.query_api()

@app.route("/api/panel/latest")
def get_latest():

    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "{MEASUREMENT}")
      |> last()
    '''

    result = query_api.query(
        org=INFLUX_ORG,
        query=query
    )

    data = {}

    for table in result:
        for record in table.records:
            data[record.get_field()] = record.get_value()

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)