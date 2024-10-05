from flask import Flask, jsonify, request  # Tambahkan 'request' di sini
from influxdb_client import InfluxDBClient

app = Flask(__name__)

# Konfigurasi InfluxDB
url = 'http://localhost:8086'
token = 'py19AVHdLHJcp0sfyXNRN0f1WkONe-BDGMaEy1XNWiDnkieN2Fl-aloDpMA727UJTVbuvGhOeY41GHc5RAYIuA=='
org = 'dcd729b34379603f'
bucket = 'airSensor-dashboard'

client = InfluxDBClient(url=url, token=token, org=org)

@app.route('/options', methods=['GET'])
def get_options():
    query = f'''
    import "influxdata/influxdb/schema"
    schema.measurements(bucket: "{bucket}")
    '''
    result = client.query_api().query(query=query)
    measurements = list(set([record["_value"] for table in result for record in table.records]))
    
    fields_query = f'''
    import "influxdata/influxdb/schema"
    schema.measurementFieldKeys(bucket: "{bucket}", measurement: "airSensors")
    '''
    fields_result = client.query_api().query(fields_query)
    fields = list(set([record["_value"] for table in fields_result for record in table.records]))

    sensor_id_query = f'''
    from(bucket: "{bucket}")
        |> range(start: -1h)
        |> distinct(column: "sensor_id")
    '''
    sensor_id_result = client.query_api().query(sensor_id_query)
    sensor_ids = list(set([record["sensor_id"] for table in sensor_id_result for record in table.records]))
    
    return jsonify({"measurements": measurements, "fields": fields, "sensor_ids": sensor_ids})

@app.route('/data', methods=['GET'])
def get_data():
    measurement = request.args.get('measurement', default="airSensors")
    field = request.args.get('field', default="co")
    sensor_id = request.args.get('sensor_id', default="TLM0100")
    
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["_field"] == "{field}")
        |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    result = client.query_api().query_data_frame(query=query)
    return jsonify(result.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)