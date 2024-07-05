#!/usr/bin/env python3

"""
@file temperature
@brief read a DHT11 temperature / humidity sensor and publish results via MQTT
@details
This is designed to run on a Raspberry Pi (any version) and poll DHT11
temperature / humidity sensor that's attached, by default, to pin 4.
If you're looking down on a Raspberry Pi, pin 4 is the top-right
pin (so, furthest from the Ethernet port).  The results are then published
to an MQTT broker.  The topic is formulated from the location, the room,
and the type of reading (temperature_f, temperature_c, humidity) separated
by forward slashes.  So, if the "location" is "home" (the default) and
the room is "test" (again, the default), then the humidity will be
published to `home/test/humidity`.
"""
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

LOCATION = os.getenv("LOCATION", "home")
ROOM = os.getenv("ROOM", "test")

mqtt_client = paho.Client()

if mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_TIMEOUT) != 0:
    logging.error("Couldn't connect to %s:%i", MQTT_HOST, MQTT_PORT)
    sys.exit(1)

while True:
    try:
        humidity, temperature_c = Adafruit_DHT.read_retry(11, PIN)
        temperature_f = temperature_c * (9 / 5) + 32

        mqtt_client.publish(f"{LOCATION}/{ROOM}/temperature_f", temperature_f)
        mqtt_client.publish(f"{LOCATION}/{ROOM}/temperature_c", temperature_c)
        mqtt_client.publish(f"{LOCATION}/{ROOM}/humidity", humidity)

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
