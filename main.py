#!/usr/bin/env python

import asyncio
import websockets
import json

@asyncio.coroutine
def hello():
    web_socket = yield from websockets.connect("wss://ws-feed.exchange.coinbase.com")
    yield from web_socket.send('{"type": "subscribe", "product_id": "BTC-USD"}')
    while True:
        message = yield from web_socket.recv()
        message = json.loads(message)
        print(message['type'])
        print("{}".format(message))
    yield from web_socket.close()

asyncio.get_event_loop().run_until_complete(hello())
