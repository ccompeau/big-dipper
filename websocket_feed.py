import asyncio
import logging
import pprint
import websockets
import json
from models import Messages, session, SQLAlchemyLogHandler

pp = pprint.PrettyPrinter(indent=4)

logger = logging.getLogger('websocket_feed_log')

handler = SQLAlchemyLogHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)



@asyncio.coroutine
def websocket_to_database():
    websocket = yield from websockets.connect("wss://ws-feed.exchange.coinbase.com")
    yield from websocket.send('{"type": "subscribe", "product_id": "BTC-USD"}')
    while True:
        message = yield from websocket.recv()
        try:
            message = json.loads(message)
        except TypeError:
            logger.error('JSON did not load, see ' + str(message))
            continue
        new_message = Messages()
        new_message.json_doc = message
        for key in message:
            if hasattr(new_message, key):
                setattr(new_message, key, message[key])
            else:
                logger.error(str(key) + ' is missing, see ' + str(message))
                continue
        session.add(new_message)
        session.commit()
    yield from websocket.close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(websocket_to_database())