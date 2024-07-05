#!/usr/bin/env python3

"""
@file temperature
@brief read a DHT11 temperature / humidity sensor and publish results via MQTT
@details
This is designed to run on a Raspberry Pi (any version) and poll DHT11
temperature / humidity sensor that's attached, by default, to pin 4.
If you're looking down on a Raspberry Pi, pin 4 is the top-right
pin (so, furthest from the Ethernet port).  The results are then published
to an MQTT broker as a JSON dict with keys of 'temperature_c',
'temperature_f', and 'humidity'.
"""

import json
import logging
import os
import sys
import time

import Adafruit_DHT
from dotenv import load_dotenv
import paho.mqtt.client as paho

load_dotenv()

PIN = int(os.getenv("PIN", "4"))
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TIMEOUT = int(os.getenv("MQTT_TIMEOUT", "60"))
READ_TIMEOUT = float(os.getenv("READ_TIMEOUT", "2.0"))
DELAY = int(os.getenv("DELAY", "3"))
TOPIC = os.getenv("TOPIC", "test")
LOG_LEVEL = int(os.getenv("LOG_LEVEL", "20"))

logging.basicConfig(level=LOG_LEVEL)

mqtt_client = paho.Client()

if mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_TIMEOUT) != 0:
    logging.error("Couldn't connect to %s:%i", MQTT_HOST, MQTT_PORT)
    sys.exit(1)

while True:
    try:
        humidity, temperature_c = Adafruit_DHT.read_retry(11, PIN)
        temperature_f = temperature_c * (9 / 5) + 32

        readings = {
            "humidity": round(humidity, 2),
            "temperature_f": round(temperature_f, 2),
            "temperature_c": round(temperature_c, 2),
        }

        readings_json = json.dumps(readings)

        logging.debug("Publishing '%s' to '%s'", readings_json, TOPIC)

        mqtt_client.publish(TOPIC, readings_json)

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        logging.info(error.args[0])
        time.sleep(READ_TIMEOUT)
        continue
    except Exception as error:
        mqtt_client.disconnect()
        raise error

    time.sleep(DELAY)

mqtt_client.disconnect()
