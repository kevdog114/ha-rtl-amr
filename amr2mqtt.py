#!/usr/bin/env python3
import subprocess
import signal
import sys
import time
import paho.mqtt.publish as publish
import settings
import json


print("Starting")
print("Meter IDs", settings.WATCHED_METERS)

# uses signal to shutdown and hard kill opened processes and self
def shutdown(signum, frame):
    subprocess.call('/usr/bin/pkill -9 rtlamr', shell=True)
    subprocess.call('/usr/bin/pkill -9 rtl_tcp', shell=True)
    subprocess.call('/usr/bin/pkill -9 amr2mqtt', shell=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

auth = None

if len(settings.MQTT_USER) and len(settings.MQTT_PASSWORD):
        auth = {'username':settings.MQTT_USER, 'password':settings.MQTT_PASSWORD}


def send_mqtt(topic, payload,):
    try:
        publish.single(topic, payload=payload, qos=1, hostname=settings.MQTT_HOST, port=settings.MQTT_PORT, auth=auth)
    except Exception as ex:
        print("MQTT Publish Failed: " + str(ex))

time.sleep(10)

# start the rtl_tcp program
rtltcp = subprocess.Popen([settings.RTL_TCP + " > /dev/null 2>&1 &"], shell=True,
    stdin=None, stdout=None, stderr=None, close_fds=True)

time.sleep(5)

# start the rtlamr program.
rtlamr = subprocess.Popen([settings.RTLAMR,
    '-msgtype=all',
    '-format=json',
    '-symbollength=' + settings.SYMBOL_LENGTH], stdout=subprocess.PIPE)

while True:
        print("Main loop")

    #try:
        # rtlamr's readline returns byte list, remove whitespace and convert to string
        amrline = rtlamr.stdout.readline().strip().decode()
        # split string on commas
        flds = json.loads(amrline)

        deviceId = 0
        consumption = 0
        if flds["Type"] == "SCM+":
            deviceId = flds["Message"]["EndpointID"]
            consumption = flds["Message"]["Consumption"]
        elif flds["Type"] == "R900":
            deviceId = flds["Message"]["ID"]
            consumption = flds["Message"]["Consumption"]
        else:
            continue

        if len(settings.WATCHED_METERS) and deviceId not in settings.WATCHED_METERS:
            continue

        print("Device={}, consumption={}".format(deviceId, consumption))

        send_mqtt(
            'readings/' + str(deviceId) + '/meter_reading',
            '%s' % (consumption)
        )

    #except:
    #    time.sleep(2)
