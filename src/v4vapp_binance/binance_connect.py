# WebSocket API Client
import json
import logging
import time

from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(module)-14s %(lineno) 5d : %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)


def message_handler(_, message):
    msg_json = json.loads(message)
    ask_price = msg_json["askPrice"]
    print(json.dumps(msg_json, indent=4, sort_keys=True))


my_client = SpotWebsocketAPIClient(on_message=message_handler)

my_client.ticker(symbol="HIVEBTC", type="FULL")
time.sleep(5)


logging.info("closing ws connection")
my_client.stop()
