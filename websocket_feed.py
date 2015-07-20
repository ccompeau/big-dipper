import asyncio
import pprint
import websockets
import json
from models import Messages, session

pp = pprint.PrettyPrinter(indent=4)

@asyncio.coroutine
def websocket_to_database():
    websocket = yield from websockets.connect("wss://ws-feed.exchange.coinbase.com")
    yield from websocket.send('{"type": "subscribe", "product_id": "BTC-USD"}')
    while True:
        message = yield from websocket.recv()
        message = json.loads(message)
        pp.pprint(message)
        new_message = Messages()
        new_message.json_doc = message
        for key in message:
            if hasattr(new_message, key):
                setattr(new_message, key, message[key])
            else:
                print(key)
                raise Exception
        session.add(new_message)
        session.commit()
    yield from websocket.close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(websocket_to_database())
