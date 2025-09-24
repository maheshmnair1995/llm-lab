import feedparser
from datetime import datetime
from database import SessionLocal
from models import NewsItem
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv

load_dotenv()

BASE_RSS = "https://news.google.com/rss"
DEFAULT_RSS = os.getenv("GOOGLE_NEWS_RSS", f"{BASE_RSS}?hl=en-US&gl=US&ceid=US:en")


def _entry_date_to_dt(parsed_time):
    if parsed_time:
        import time
        return datetime.fromtimestamp(time.mktime(parsed_time))
    return None


def _store_entries(entries, limit=50):
    session = SessionLocal()
    added = 0
    fetched = min(len(entries), limit)
    for entry in entries[:limit]:
        guid = entry.get("id") or entry.get("guid") or entry.get("link")
        title = entry.get("title", "")
        link = entry.get("link", "")
        published = _entry_date_to_dt(entry.get("published_parsed"))
        summary = entry.get("summary", "") or entry.get("description", "")
        source = entry.get("source", {}).get("title", "") if isinstance(entry.get("source"), dict) else ""
        item = NewsItem(
            guid=guid,
            title=title,
            link=link,
            published=published,
            summary=summary,
            source=source
        )
        try:
            session.add(item)
            session.commit()
            added += 1
        except IntegrityError:
            session.rollback()
        except Exception:
            session.rollback()
    session.close()
    return {"fetched": fetched, "added": added}


def fetch_and_store(limit: int = 50):
    """Fetch general news from default RSS and store."""
    d = feedparser.parse(DEFAULT_RSS)
    return _store_entries(d.entries, limit)


def fetch_and_store_topic(topic: str, limit: int = 50):
    """
    Fetch news for a specific search topic (Google News RSS query).
    Example: https://news.google.com/rss/search?q=bitcoin&hl=en-US&gl=US&ceid=US:en
    """
    url = f"{BASE_RSS}/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
    d = feedparser.parse(url)
    return _store_entries(d.entries, limit)
