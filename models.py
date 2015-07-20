from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from urllib.parse import quote
from config import DB_PASSWORD

engine = create_engine("postgresql://pierre:%s@localhost/bigdipper" % quote(DB_PASSWORD))

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

class Messages(Base):
    __tablename__ = 'messages'

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


if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
