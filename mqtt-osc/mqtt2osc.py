import argparse
import json
import os

import paho.mqtt.client as mqtt
from pythonosc import udp_client


class MQTTtoOSC:
    def __init__(
        self,
        mqtt_broker,
        mqtt_port,
        mqtt_topic,
        osc_host,
        osc_port,
        username=None,
        password=None,
    ):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic

        # Initialize OSC client
        self.osc_client = udp_client.SimpleUDPClient(osc_host, osc_port)

        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        if username and password:
            print("Connecting with username and password")
            self.mqtt_client.username_pw_set(username, password)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")

        if rc != 0:
            return

        # Subscribe to topic on connect
        if isinstance(self.mqtt_topic, list):
            if len(self.mqtt_topic) == 0:
                print("Warning: no topics provided!")
                return

            for topic in self.mqtt_topic:
                client.subscribe(topic)
                print(f"Subscribed to {topic}")
        else:
            client.subscribe(self.mqtt_topic)
            print(f"Subscribed to topic: {self.mqtt_topic}")

    def on_message(self, client, userdata, msg):
        print(f"= Received MQTT message on {msg.topic}: {msg.payload.decode()}")

        def unpackDict(path, data, char="/"):
            paths = []
            if isinstance(data, dict):
                for key, value in data.items():
                    paths.extend(unpackDict(path + char + key, value, char))
            else:
                paths.append((path, data))

            return paths

        # Parse the MQTT message
        try:
            # Try to parse as JSON
            data = json.loads(msg.payload.decode())

            # Send to OSC - you can customize the OSC address
            osc_address = f"/{msg.topic.replace('/', '_')}"

            msgs = unpackDict(osc_address, data)

            for m, value in msgs:
                print(f"{m} {value}")
                self.osc_client.send_message(m, value)

        except json.JSONDecodeError:
            # If not JSON, send as plain string
            osc_address = f"/{msg.topic.replace('/', '_')}"
            self.osc_client.send_message(osc_address, msg.payload.decode())
            # print(f"{osc_address}", msg.payload.decode())

        # print(f"Forwarded to OSC: {osc_address}")

    def start(self):
        # Connect to MQTT broker
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)

        # Start the MQTT loop
        print("Starting MQTT to OSC bridge...")
        self.mqtt_client.loop_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MQTT to OSC Bridge")
    parser.add_argument(
        "--mqtt-broker",
        default=os.getenv("MQTT_HOST", "localhost"),
        help="MQTT broker address",
    )
    parser.add_argument(
        "--mqtt-port",
        default=os.getenv("MQTT_PORT", "1883"),
        type=int,
        help="MQTT broker port",
    )
    parser.add_argument(
        "--mqtt-topic",
        default=os.getenv("MQTT_TOPIC", "#"),
        nargs="*",
        help="MQTT topic(s) to subscribe to (# for all)",
    )
    parser.add_argument(
        "--mqtt-username",
        default=os.getenv("MQTT_USERNAME", None),
        help="MQTT broker username.",
    )
    parser.add_argument(
        "--mqtt-password",
        default=os.getenv("MQTT_PASSWORD", None),
        help="MQTT broker password.",
    )
    parser.add_argument(
        "--osc-host",
        default=os.getenv("OSC_HOST", "127.0.0.1"),
        help="OSC destination host",
    )
    parser.add_argument(
        "--osc-port",
        type=int,
        default=os.getenv("OSC_PORT", "5000"),
        help="OSC destination port",
    )

    args = parser.parse_args()

    print(args)

    bridge = MQTTtoOSC(
        mqtt_broker=args.mqtt_broker,
        mqtt_port=args.mqtt_port,
        mqtt_topic=args.mqtt_topic,
        osc_host=args.osc_host,
        osc_port=args.osc_port,
        username=args.mqtt_username,
        password=args.mqtt_password,
    )

    bridge.start()
