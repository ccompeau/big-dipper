#!/usr/bin/env python

import asyncio
import pprint
import websockets
import json
from models import Messages, session

pp = pprint.PrettyPrinter(indent=4)

@asyncio.coroutine
def hello():
    web_socket = yield from websockets.connect("wss://ws-feed.exchange.coinbase.com")
    yield from web_socket.send('{"type": "subscribe", "product_id": "BTC-USD"}')
    while True:
        message = yield from web_socket.recv()
        message = json.loads(message)
        new_message = Messages()
        new_message.json_doc = message
        for key in message:
            if hasattr(new_message, key):
                setattr(new_message, key, message[key])
            else:
                pp.pprint(message)
                print(key)
                raise Exception
        session.add(new_message)
        session.commit()
    yield from web_socket.close()

asyncio.get_event_loop().run_until_complete(hello())
