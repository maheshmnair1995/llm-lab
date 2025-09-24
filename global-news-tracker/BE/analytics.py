from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from database import SessionLocal
from models import NewsItem
import pandas as pd
import re
from collections import Counter


def clean_text(t: str) -> str:
    if not t:
        return ""
    t = re.sub(r"http\S+", "", t)
    t = re.sub(r"[^A-Za-z0-9\s]", " ", t)
    return t.lower()


def compute_topics(n_clusters: int = 5, lookback: int = 200):
    """
    Returns dict ready for colorful charts:
    {
      "topics": [ {cluster, top_terms, count} ... ],
      "counts": {cluster: count, ...},
      "labels": ["Topic 0: climate, change", "Topic 1: bitcoin, crypto", ...],
      "distribution": [30, 20, 50]
    }
    """
    session = SessionLocal()
    items = session.query(NewsItem).order_by(NewsItem.published.desc()).limit(lookback).all()
    session.close()
    if not items:
        return {"topics": [], "counts": {}, "labels": [], "distribution": []}

    df = pd.DataFrame([{
        "id": i.id,
        "title": i.title or "",
        "summary": i.summary or "",
        "text": f"{i.title or ''}. {i.summary or ''}"
    } for i in items])
    df["text_clean"] = df["text"].apply(clean_text)

    vec = TfidfVectorizer(max_df=0.9, min_df=1, stop_words="english", ngram_range=(1, 2))
    X = vec.fit_transform(df["text_clean"])

    if X.shape[0] < n_clusters:
        n_clusters = max(1, X.shape[0] // 2) or 1

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    df["cluster"] = labels

    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vec.get_feature_names_out()
    topics = []
    counts = Counter(labels)

    label_list = []
    dist = []
    for i in range(n_clusters):
        top_terms = [terms[ind] for ind in order_centroids[i, :8] if ind < len(terms)]
        label_str = f"Topic {i}: {', '.join(top_terms[:3])}"
        topics.append({"cluster": int(i), "top_terms": top_terms, "count": int(counts.get(i, 0))})
        label_list.append(label_str)
        dist.append(int(counts.get(i, 0)))

    counts_dict = {str(k): int(v) for k, v in counts.items()}
    return {
        "topics": topics,
        "counts": counts_dict,
        "labels": label_list,
        "distribution": dist
    }
