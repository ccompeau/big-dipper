import logging
import traceback
from sqlalchemy import create_engine, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer, Numeric, String

from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

class Messages(Base):
    __tablename__ = 'coinbase_messages'

    sequence = Column(Integer, primary_key=True)
    type = Column(String)
    message = Column(String)
    time = Column(DateTime(timezone=True))
    product_id = Column(String)
    order_id = Column(String)
    taker_order_id = Column(String)
    maker_order_id = Column(String)
    reason = Column(String)
    trade_id = Column(Integer)
    funds = Column(Numeric)
    size = Column(Numeric)
    remaining_size = Column(Numeric)
    price = Column(Numeric)
    side = Column(String)
    order_type = Column(String)
    client_oid = Column(String)
    json_doc = Column(JSONB, unique=True)


class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    logger = Column(String)
    level = Column(String)
    trace = Column(String)
    msg = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Log: %s - %s>" % (self.created_at.strftime('%m/%d/%Y-%H:%M:%S'), self.msg[:50])


class SQLAlchemyLogHandler(logging.Handler):
    def emit(self, record):
        log = Log()
        log.logger = record.__dict__['name']
        log.level = record.__dict__['levelname']
        exc = record.__dict__['exc_info']
        if exc:
            log.trace = traceback.format_exc(exc)
        else:
            log.trace = None
        log.msg = record.__dict__['msg']
        session.add(log)
        session.commit()


if __name__ == "__main__":
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
