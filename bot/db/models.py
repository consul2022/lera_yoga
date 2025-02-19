from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, DateTime

from bot.db.db import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)
    fullname = Column(String)


class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'))
    channel_id = Column(BigInteger)
    start_date = Column(DateTime)
    finish_date = Column(DateTime)
