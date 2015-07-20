import threading
from datetime import datetime, timedelta
import pytz
from sqlalchemy import func
from models import session, Messages
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from twython import Twython
from config import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

minutes = 1/60

utc = pytz.utc


def run():
    now = datetime.utcnow()
    utc.localize(now)
    five_minutes_ago = now - timedelta(minutes=5)
    type, five_minute_moving_average = (session.query(Messages.type, func.avg(Messages.price))
                                        .filter(Messages.type == "match")
                                        .filter(Messages.time.op('AT TIME ZONE')('UTC').between(five_minutes_ago, now))
                                        .group_by(Messages.type).one())
    twenty_four_hours_ago = now - timedelta(days=1)
    type, twenty_four_hour_moving_average = (session.query(Messages.type, func.avg(Messages.price))
                                             .filter(Messages.type == "match")
                                             .filter(
        Messages.time.op('AT TIME ZONE')('UTC').between(twenty_four_hours_ago, now))
                                             .group_by(Messages.type).one())
    change = five_minute_moving_average - twenty_four_hour_moving_average
    percent_change = change / twenty_four_hour_moving_average

    price_series = (session.query(Messages.time, Messages.price, Messages.size)
                    .filter(Messages.type == "match")
                    .filter(Messages.time.op('AT TIME ZONE')('UTC').between(twenty_four_hours_ago, now))
                    .order_by(Messages.time)
                    .all())
    fig, ax = plt.subplots()
    time, price, volume = zip(*price_series)
    ax.plot(time, price)
    ax.xaxis.set_major_locator(mdates.HourLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator())
    plt.gcf().autofmt_xdate()
    ax.format_xdata = mdates.DateFormatter('%H')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.3, top=0.9)
    plt.savefig('foo.png')
    plt.close()
    tweet_text = "24 hour moving average: {1:.2f}\n" \
                 "5 min moving average: {0:.2f}\n" \
                 "Percent change: {2:.2%}\n" \
                 "#Bitcoin".format(five_minute_moving_average,
                                   twenty_four_hour_moving_average,
                                   percent_change)
    photo = open('foo.png', 'rb')
    response = twitter.upload_media(media=photo)
    twitter.update_status(status=tweet_text, media_ids=[response['media_id']])
    session.close()
    threading.Timer(60 * minutes, run).start()

threading.Timer(60 * minutes, run).start()
