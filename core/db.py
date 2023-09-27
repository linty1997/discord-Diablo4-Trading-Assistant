from .models import Session, Trading
from datetime import datetime, timedelta
import uuid


class BaseDB:
    def __init__(self):
        self.db = Session().get_db()
        self.now_time = datetime.utcnow()
        self.now_timestamp = datetime.utcnow().timestamp()

    def close(self):
        self.db.close()


class TradingDB(BaseDB):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.user = None

    def upsert(self, trading):
        existing = self.db.query(Trading).filter(Trading.id == trading.id).first()
        if existing:
            for key, value in trading.__dict__.items():
                setattr(existing, key, value)
        else:
            self.db.add(trading)
        self.db.commit()
        self.db.refresh(trading)
        return trading

    def get_trading(self, ctx, trading_id, close=False):
        status = "1"
        if close:
            status = "0"
        if not isinstance(trading_id, bytes):
            trading_id = uuid.UUID(trading_id).bytes
        return self.db.query(Trading).filter(Trading.id == trading_id, Trading.status == status,
                                             Trading.creator_id == ctx.user.id).first()

    def get_trading_by_message_id(self, message_id):
        return self.db.query(Trading).filter(Trading.message_id == message_id).first()

    def get_tradings(self):
        return self.db.query(Trading).filter(Trading.status == "1").all()

    def get_tradings_by_user(self, user_id):
        return self.db.query(Trading).filter(Trading.creator_id == user_id,
                                             Trading.status == "1").all()
