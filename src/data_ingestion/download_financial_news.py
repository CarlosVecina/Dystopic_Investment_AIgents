import argparse
import json
import os
import websocket 
from dotenv import load_dotenv
import rel

from src.data_ingestion.kafka.base_producer import BaseProducer


load_dotenv()

auth_msg = {
  "action": "auth",
  "key": os.environ["APCA_API_KEY_ID"],
  "secret": os.environ["APCA_API_SECRET_KEY"]
}

m = {
  "action": "listen",
  "data": {
    "streams": ["trade_updates"]
  }
}


def on_message(ws, message):
    producer = BaseProducer(bootstrap_servers=os.environ["BOOSTRAP_BROKER"], sasl_mechanism="PLAIN")
    producer.produce("news-topic", "key", message.hex())
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    ws.send(json.dumps(auth_msg))
    ws.send(json.dumps(m))
    print("Opened connection")

if __name__ == "__main__":
    parser=argparse.ArgumentParser()

    parser.add_argument("--url", help="Socker url")

    args=parser.parse_args()

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(args.url, #"wss://api.gemini.com/v1/marketdata/BTCUSD",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    ws.run_forever(dispatcher=rel, reconnect=5)
    rel.signal(2, rel.abort)
    rel.dispatch()
