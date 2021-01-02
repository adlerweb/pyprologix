#!/usr/bin/env python3

# Poll Multimeters 23 and 24 every second, send data to local InfluxDB

#Folder with hp3478a.py/prologix.py must be in PYTHONPATH
#Alternatively copy them to this folder
from influxdb import InfluxDBClient
from hp3478a import hp3478a
import sched, time
s = sched.scheduler(time.time, time.sleep)

port = "/dev/ttyACM0"

multimeter1 = hp3478a(23, port, debug=True)
multimeter2 = hp3478a(24, prologixGpib=multimeter1.gpib, debug=True)

client = InfluxDBClient(host='localhost', port=8086, database='multimeter')

def pollData(sc): 
    json_body = []

    try:
        multimeter1.getStatus()
        measurement = float(multimeter1.getMeasure())

        json_body.append(
            {
                "measurement": "measurement",
                "tags": {
                    "id": 22,
                    "type": multimeter1.getFunction()
                },
                "fields": {
                    "measurement": measurement,
                    "range": multimeter1.getRange(numeric=True),
                }
            })
    except:
        pass

    try:
        multimeter2.getStatus()
        measurement2 = float(multimeter2.getMeasure())

        json_body.append(
            {
                "measurement": "measurement",
                "tags": {
                    "id": 21,
                    "type": multimeter2.getFunction()
                },
                "fields": {
                    "measurement": measurement2,
                    "range": multimeter2.getRange(numeric=True),
                }
            })
    except:
        pass

    print(json_body)
    client.write_points(json_body)
    s.enter(1, 1, pollData, (sc,))

s.enter(1, 1, pollData, (s,))
s.run()


