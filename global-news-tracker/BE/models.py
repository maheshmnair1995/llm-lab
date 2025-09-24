from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
import datetime

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = "news_items"
    id = Column(Integer, primary_key=True, index=True)
    guid = Column(String(512), unique=True, index=True, nullable=True)
    title = Column(String(1024))
    link = Column(String(2048))
    published = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    source = Column(String(256), nullable=True)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
    summarized = Column(Boolean, default=False)
    summary_text = Column(Text, nullable=True)
