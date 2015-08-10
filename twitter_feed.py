import threading
from datetime import datetime, timedelta
import logging

import pytz
from sqlalchemy import func
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm.exc import NoResultFound
from matplotlib import pyplot, dates

from twython import Twython

from models import session, Messages, SQLAlchemyLogHandler
from config import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

minutes = 5

utc = pytz.utc

logger = logging.getLogger('twitter_feed_log')

handler = SQLAlchemyLogHandler()
handler.setLevel(logging.INFO)

logger.addHandler(handler)
logger.setLevel(logging.INFO)

def run():
    now = datetime.utcnow()
    utc.localize(now)
    five_minutes_ago = now - timedelta(minutes=5)
    ten_minutes_ago = now - timedelta(minutes=10)
    twenty_four_hours_ago = now - timedelta(days=1)

    try:
        five_minute_moving_average, = (session.query(func.avg(Messages.price))
                                      .filter(Messages.type == "match")
                                      .filter(Messages.time.op('AT TIME ZONE')('UTC').between(five_minutes_ago, now))
                                      .group_by(Messages.type).one())
    except NoResultFound:
        logger.error('Twitter feed log: no results found for 5 minute moving average.')
        threading.Timer(60 * minutes, run).start()
        return
    except DatabaseError:
        # TODO add text log for database errors
        # logger.error('Twitter feed log: database error.')
        threading.Timer(60 * minutes, run).start()
        return

    try:
        last_five_minute_moving_average, = (session.query(func.avg(Messages.price))
                                      .filter(Messages.type == "match")
                                      .filter(Messages.time.op('AT TIME ZONE')('UTC').between(ten_minutes_ago, five_minutes_ago))
                                      .group_by(Messages.type).one())
    except NoResultFound:
        logger.error('Twitter feed log: no results found for last 5 minute moving average.')
        threading.Timer(60 * minutes, run).start()
        return
    except DatabaseError:
        # logger.error('Twitter feed log: database error.')
        threading.Timer(60 * minutes, run).start()
        return

    try:
        twenty_four_hour_moving_average, = (session.query(func.avg(Messages.price))
                                           .filter(Messages.type == "match")
                                           .filter(Messages.time.op('AT TIME ZONE')('UTC').between(twenty_four_hours_ago, now))
                                           .group_by(Messages.type).one())
    except NoResultFound:
        logger.error('Twitter feed log: no results found for 24 hour moving average.')
        threading.Timer(60 * minutes, run).start()
        return
    except DatabaseError:
        # logger.error('Twitter feed log: database error.')
        threading.Timer(60 * minutes, run).start()
        return

    this_change = (five_minute_moving_average - twenty_four_hour_moving_average)/twenty_four_hour_moving_average
    last_change = (last_five_minute_moving_average - twenty_four_hour_moving_average)/twenty_four_hour_moving_average
    tweet_text = "24 hour moving average: {1:.2f}\n" \
                 "5 min moving average: {0:.2f}\n" \
                 "Percent change: {2:.2%}\n" \
                 "#Bitcoin".format(five_minute_moving_average,
                                   twenty_four_hour_moving_average,
                                   this_change)

    logger.info(tweet_text)
    if (this_change > 0.05 or this_change < -0.05) and not (last_change > 0.05 or last_change < -0.05):
        try:
            price_series = (session.query(Messages.time, Messages.price, Messages.size)
                            .filter(Messages.type == "match")
                            .filter(Messages.time.op('AT TIME ZONE')('UTC').between(twenty_four_hours_ago, now))
                            .order_by(Messages.time)
                            .all())
        except DatabaseError:
            threading.Timer(60 * minutes, run).start()
            return
        fig, ax = pyplot.subplots()
        time, price, volume = zip(*price_series)
        ax.plot(time, price)
        ax.xaxis.set_major_locator(dates.HourLocator())
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H'))
        ax.xaxis.set_minor_locator(dates.MinuteLocator())
        pyplot.gcf().autofmt_xdate()
        ax.format_xdata = dates.DateFormatter('%H')
        pyplot.subplots_adjust(left=0.1, right=0.9, bottom=0.3, top=0.9)
        pyplot.savefig('foo.png')
        pyplot.close()
        photo = open('foo.png', 'rb')
        response = twitter.upload_media(media=photo)
        twitter.update_status(status=tweet_text, media_ids=[response['media_id']])
    else:
        threading.Timer(60 * minutes, run).start()
        return
    session.close()
    threading.Timer(60 * minutes, run).start()


threading.Timer(1, run).start()
