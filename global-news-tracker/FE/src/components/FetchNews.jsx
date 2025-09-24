import React, { useState } from "react";
import axios from "axios";

export default function FetchNews() {
  const [status, setStatus] = useState(null);
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState(""); // client-side filter
  const [topic, setTopic] = useState("");   // backend topic search

  const API_BASE = "http://localhost:5001/api";

  // Fetch latest headlines from default RSS
  const onFetch = async () => {
    setStatus("Fetching latest news...");
    try {
      const r = await axios.post(`${API_BASE}/fetch_news`, { limit: 50 });
      setStatus(`Fetched ${r.data.result.fetched}, added ${r.data.result.added}`);
      loadNews();
    } catch (err) {
      setStatus("Error: " + (err?.message || String(err)));
    }
  };

  // Load stored news (all)
  const loadNews = async () => {
    try {
      const r = await axios.get(`${API_BASE}/news?page=1&per=50`);
      setItems(r.data.items || []);
      setStatus(`Loaded ${r.data.items.length} stored news items`);
    } catch (err) {
      setStatus("Error: " + (err?.message || String(err)));
    }
  };

  // Search stored news client-side
  const filteredItems = items.filter(
    (it) =>
      it.title.toLowerCase().includes(search.toLowerCase()) ||
      (it.summary_text || "").toLowerCase().includes(search.toLowerCase())
  );

  // Search news by topic via backend
  const searchByTopic = async () => {
    if (!topic) return;
    setStatus(`Searching news for topic: ${topic}`);
    try {
      // Fetch topic news from Google News RSS
      await axios.post(`${API_BASE}/search_news`, { topic, limit: 50 });

      // Load news filtered by topic from database
      const r = await axios.get(
        `${API_BASE}/news?page=1&per=50&topic=${encodeURIComponent(topic)}`
      );
      setItems(r.data.items || []);
      setStatus(`Loaded ${r.data.items.length} news items for topic "${topic}"`);
    } catch (err) {
      setStatus("Error: " + (err?.message || String(err)));
    }
  };

  return (
    <div className="panel">
      <h2>Fetch Latest Headlines</h2>

      <div>
        <button onClick={onFetch}>Fetch from Google News RSS</button>
        <button onClick={loadNews} style={{ marginLeft: 8 }}>
          Load Stored News
        </button>
      </div>

      <div style={{ marginTop: 10 }}>
        <strong>Status:</strong> {status}
      </div>

      {/* 🔎 Client-side search among loaded news */}
      <div style={{ marginTop: 10 }}>
        <input
          type="text"
          placeholder="Search loaded news..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: "6px", width: "60%", marginRight: 8 }}
        />
      </div>

      {/* 🔍 Search by topic via backend */}
      <div style={{ marginTop: 10 }}>
        <input
          type="text"
          placeholder="Search news by topic..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          style={{ padding: "6px", width: "60%", marginRight: 8 }}
        />
        <button onClick={searchByTopic}>Search Topic</button>
      </div>

      <div className="news-list" style={{ marginTop: 15 }}>
        {filteredItems.map((it) => (
          <div key={it.id} className="news-item">
            <a href={it.link} target="_blank" rel="noreferrer">
              {it.title}
            </a>
            <div className="meta">
              {it.published} • summarized: {String(it.summarized)}
            </div>
            {it.summary_text && <blockquote>{it.summary_text}</blockquote>}
          </div>
        ))}
      </div>
    </div>
  );
}
