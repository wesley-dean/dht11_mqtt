# DHT11 to MQTT Publisher

This tool is designed to run from a Raspberry Pi with a DHT11
temperature / humidity sensor attached to pin 4 (top-right pin,
furthest from the Ethernet port) and publish the results to
an MQTT broker.

For a good walkthrough about the wiring of the sensor, how to
interact with the sensor using C, check out
[Scott Campbell](https://www.circuitbasics.com/author/circuitbasicsgmail-com/)
's
[article](https://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/)
.  It looks like the article was written in 2016; however, the
diagrams are still correct.  The sample Python code is written
for Python 2 (which has since been deprecated); updating it for Python 3
takes seconds..  like 5 of them.

## Configuration

The tool is configured with a series of environment variables; however, in
the probable event that it's inconvenient to set a bunch of variables every
time the tool is used, a `.env` file is supported and a sample is provided
with the tool's defaults.

* **PIN**: the pin on the GPIO where the signal wire is connected
  default: 4
* **MQTT_HOST**: the MQTT broker's hostname or IP address
  default: 127.0.0.1 (localhost)
* **MQTT_PORT**: the port on the MQTT broker listening for traffic
  default: 1883 (unencrypted)
* **MQTT_TIMEOUT**: MQTT broker connection timeout before failing
  default: 60 (seconds)
* **READ_TIMEOUT**: in the event of a read error, how long to wait efore retry
  default: 2 (seconds)
* **DELAY**: how long between successful reads before looping
  default: 60 (seconds)
* **LOCATION**: alphanumeric descriptor of the location of sensor
  default: home
* **ROOM**: alphanumeric description of the room for the sensor
  default: test

## Setup

The tool is a simple Python script.  Included in this repository
is a `requirements.txt` file that lists the modules that are used
to support the tool.  Therefore, before running the tool the
first time, install the requirements with:

```sh
pip3 install -r ./requirements.txt
```

## Updates

It is possible that there are updates to this tool, most likely
as a result of dependency updates.  In that case, the tool can
be updated with:

```sh
git pull origin main
pip3 install -r ./requirements.txt
```

## Running the Tool

The tool is a simple Python script, so it can be run with:

```sh
python3 ./temperature.py
```

This will start the tool in the foreground and it'll run
until stopped (control-c or SIGINT).

### Running the Tool at Startup

A hackish, "just make it go" way of having the tool start
at boot at just run in the background is:

```crontab
@reboot while true ; do "${HOME}/dht11_mqtt/temperature.py" ; sleep 5 ; done
```

Add that line to your crontab (`crontab -e`), reboot, and you're
good to go.

## Using Home Assistant

My use-case for this project was feeding temperature data to a
[Home Assistant](https://home-assistant.io/) instance through an
MQTT broker.  Earlier iterations of this project exposed a
RESTful API which, when queried, would return a JSON object with
the data.  The pulling / polling approach had a number of challenges
and having [Flask](https://flask.palletsprojects.com/en/3.0.x/)
listen for traffic... it was all more work than it was worth,
especially when the Raspberry Pi was offline or the sensor was
being weird or whatever.

So, this project was an MQTT-based refactor that allowed
Home Assistant to subscribe to topics populated with data
published by this tool.

The MQTT broker used when developing this tool was 
[Eclipse Mosquitto](https://mosquitto.org/).  Home Assistant
provides an
[MQTT Broker add-on](https://github.com/home-assistant/hassio-addons/blob/master/mosquitto/DOCS.md)
that works very well.  Moreover, Home Assistant provides
[documentation for integrating with Mosquitto](https://www.home-assistant.io/integrations/mqtt)
.
