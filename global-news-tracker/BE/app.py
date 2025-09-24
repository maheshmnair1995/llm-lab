from flask import Flask, jsonify, request
from flask_cors import CORS
from database import engine, SessionLocal
from models import Base, NewsItem
from news_fetcher import fetch_and_store, fetch_and_store_topic
from summarizer import summarize_text
from analytics import compute_topics
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app)


@app.route("/api/fetch_news", methods=["POST"])
def api_fetch_news():
    body = request.json or {}
    limit = int(body.get("limit", 50))
    result = fetch_and_store(limit=limit)
    return jsonify({"status": "ok", "result": result})


@app.route("/api/search_news", methods=["POST"])
def api_search_news():
    """
    Fetch and store news for a custom topic.
    Body: { "topic": "bitcoin", "limit": 30 }
    """
    body = request.json or {}
    topic = body.get("topic")
    if not topic:
        return jsonify({"error": "topic required"}), 400
    limit = int(body.get("limit", 50))
    result = fetch_and_store_topic(topic=topic, limit=limit)
    return jsonify({"status": "ok", "topic": topic, "result": result})


@app.route("/api/news", methods=["GET"])
def api_list_news():
    page = int(request.args.get("page", 1))
    per = int(request.args.get("per", 30))
    topic = request.args.get("topic", "").lower()  # new
    session = SessionLocal()
    
    query = session.query(NewsItem).order_by(NewsItem.published.desc().nullslast())
    
    if topic:
        query = query.filter(
            (NewsItem.title.ilike(f"%{topic}%")) | (NewsItem.summary.ilike(f"%{topic}%"))
        )
    
    total = query.count()
    items = query.offset((page - 1) * per).limit(per).all()
    session.close()

    data = []
    for i in items:
        data.append({
            "id": i.id,
            "guid": i.guid,
            "title": i.title,
            "link": i.link,
            "published": i.published.isoformat() if i.published else None,
            "summary": i.summary,
            "summarized": bool(i.summarized),
            "summary_text": i.summary_text
        })
    return jsonify({"total": total, "page": page, "per": per, "items": data})


@app.route("/api/summarize/<int:news_id>", methods=["POST"])
def api_summarize(news_id):
    with SessionLocal() as session:
        item = session.query(NewsItem).get(news_id)
        if not item:
            return jsonify({"error": "not found"}), 404

        content = (item.summary or "") + "\n\n" + (item.title or "")
        summary = summarize_text(item.title or "", content)
        item.summary_text = summary
        item.summarized = True
        session.add(item)
        session.commit()
        return jsonify({"id": item.id, "summary": summary})


@app.route("/api/analytics/topics", methods=["GET"])
def api_topics():
    clusters = int(request.args.get("clusters", 5))
    result = compute_topics(n_clusters=clusters)
    return jsonify(result)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


if __name__ == "__main__":
    app.run(port=5001, host="0.0.0.0")
