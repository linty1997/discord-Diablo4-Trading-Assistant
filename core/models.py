from sqlalchemy import Column, String, DateTime, func, BigInteger, Text, Float, Boolean
from sqlalchemy.dialects.mysql import BINARY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.types import TypeDecorator, Text
import json
import uuid
import os

Base = declarative_base()


# Session
class Session:
    def __init__(self):
        self.engine_url = os.getenv('DB_URL')
        self.engine = create_engine(self.engine_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def get_db(self):
        return self.Session()


# JSONDict
class JSONDict(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# Trading Model
class Trading(Base):
    __tablename__ = 'trading'

    id = Column(BINARY(16), primary_key=True, default=uuid.uuid4().bytes)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    creator_id = Column(BigInteger)
    message_id = Column(BigInteger, nullable=True)
    trading_embed = Column(JSONDict, nullable=True)
    version = Column(BigInteger)
    item_type = Column(String(32))
    status = Column(Boolean, default=False)
    title = Column(String(128))
    image_url = Column(JSONDict, nullable=True)
    content = Column(JSONDict)
    end_time = Column(TIMESTAMP, nullable=True)
    start_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    last_bidder_id = Column(BigInteger, nullable=True)


