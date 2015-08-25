import asyncio
import logging
from logging.handlers import RotatingFileHandler
import pprint
import json
import random
from sqlalchemy.exc import IntegrityError, DatabaseError
import time

import websockets

from models import Messages, session, SQLAlchemyLogHandler

pp = pprint.PrettyPrinter(indent=4)

db_logger = logging.getLogger('websocket_feed_log')
file_logger = logging.getLogger('database_csv')

db_handler = SQLAlchemyLogHandler()
db_handler.setLevel(logging.INFO)
db_logger.addHandler(db_handler)
db_logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler('database_log.csv', 'a', 10 * 1024 * 1024, 100)
file_handler.setFormatter(logging.Formatter('%(asctime)s, %(levelname)s, %(message)s'))
file_handler.setLevel(logging.INFO)
file_logger.addHandler(file_handler)

websocket_logger = logging.getLogger('websockets')
websocket_logger.addHandler(db_handler)
websocket_logger.setLevel(logging.INFO)


@asyncio.coroutine
def websocket_to_database():
    websocket = yield from websockets.connect("wss://ws-feed.exchange.coinbase.com")
    yield from websocket.send('{"type": "subscribe", "product_id": "BTC-USD"}')
    while True:
        message = yield from websocket.recv()
        if message is None:
            file_logger.error('Websocket message is None!')
            break
        try:
            message = json.loads(message)
        except TypeError:
            db_logger.error('JSON did not load, see ' + str(message))
            continue
        new_message = Messages()
        for key in message:
            if hasattr(new_message, key):
                setattr(new_message, key, message[key])
            else:
                db_logger.error(str(key) + ' is missing, see ' + str(message))
                continue
        try:
            session.add(new_message)
            session.commit()
        except IntegrityError:
            db_logger.error('Integrity error, see ' + str(message))
            session.rollback()
        except DatabaseError:
            file_logger.error('Database Error')
            session.rollback()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    n = 0
    while True:
        n += 1
        time.sleep((2 ** n) + (random.randint(0, 1000) / 1000))
        loop.run_until_complete(websocket_to_database())
        if n > 6:
            n = 0