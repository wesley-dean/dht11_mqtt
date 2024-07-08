#!/usr/bin/env python3

"""
@file temperature
@brief read a DHT11 temperature / humidity sensor and publish results via MQTT
@details
This is designed to run on a Raspberry Pi (any version) and poll DHT11
temperature / humidity sensor that's attached, by default, to pin 4.
The results are then published to an MQTT broker as a JSON dict with keys
of 'temperature_c', 'temperature_f', and 'humidity'.
"""

from datetime import datetime, timezone
import json
import logging
import os
import sys
import time

import Adafruit_DHT
from dotenv import load_dotenv
import paho.mqtt.client as paho

load_dotenv()

##
# @var int PIN
# @brief the GPIO pin used for signalling
PIN = int(os.getenv("PIN", "4"))

##
# @var str MQTT_HOST
# @brief the hostname or IP address of the MQTT broker
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")

##
# @var int PORT
# @brief the port the MQTT broker is listening on
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

##
# @var int MQTT_TIMEOUT
# @brief maximum seconds between interactions with the MQTT broker
# @details
# After this many seconds, if there hasn't been an interaction
# with the MQTT broker, send a keep-alive message
MQTT_TIMEOUT = int(os.getenv("MQTT_TIMEOUT", "60"))

##
# @var float READ_TIMEOUT
# @brief in the event a read error, wait this many seconds before retry
READ_TIMEOUT = float(os.getenv("READ_TIMEOUT", "2.0"))

##
# @var int DELAY
# @brief how long between successful reads to sleep
DELAY = int(os.getenv("DELAY", "3"))

##
# @var str TOPIC
# @brief the topic where messages should be published
TOPIC = os.getenv("TOPIC", "test")

##
# @var int LOG_LEVEL
# @brief how verbose to be (10 is most verbose, 50 is least)
LOG_LEVEL = int(os.getenv("LOG_LEVEL", "20"))

##
# @var int LOOPS
# @brief how many times to read or <= 0 for infinite
LOOPS = int(os.getenv("LOOPS", "0"))

logging.basicConfig(level=LOG_LEVEL)


def main():
    """
    @fn main
    @brief main function
    """

    mqtt_client = paho.Client()

    loop_count = 0

    if mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_TIMEOUT) != 0:
        logging.error("Couldn't connect to %s:%i", MQTT_HOST, MQTT_PORT)
        sys.exit(1)

    while (LOOPS <= 0) or (loop_count >= LOOPS):
        try:
            humidity, temperature_c = Adafruit_DHT.read_retry(11, PIN)
            temperature_f = temperature_c * (9 / 5) + 32
            now = datetime.now(timezone.utc)

            readings = {
                "humidity": round(humidity, 2),
                "temperature_f": round(temperature_f, 2),
                "temperature_c": round(temperature_c, 2),
                "timestamp_utc": now,
            }

            readings_json = json.dumps(readings)

            logging.debug("Publishing '%s' to '%s' at %s", readings_json, TOPIC, now)

            mqtt_client.publish(TOPIC, readings_json)

        except RuntimeError as error:
            # in the event of a read error, delay and then try again
            logging.info(error.args[0])
            time.sleep(READ_TIMEOUT)
            continue
        except Exception as error:
            mqtt_client.disconnect()
            raise error

        time.sleep(DELAY)

    mqtt_client.disconnect()


if __name__ == "__main__":
    main()
