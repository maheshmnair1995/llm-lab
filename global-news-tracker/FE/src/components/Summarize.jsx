import React, { useEffect, useState } from "react";
import { listNews, summarize } from "../api";

export default function Summarize() {
  const [items, setItems] = useState([]);
  const [loadingId, setLoadingId] = useState(null);
  const [search, setSearch] = useState("");

  const load = async () => {
    try {
      const r = await listNews(1, 50);
      setItems(r.data.items || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const doSummarize = async (id) => {
    setLoadingId(id);
    try {
      const r = await summarize(id);
      setItems(
        items.map((it) =>
          it.id === id
            ? { ...it, summary_text: r.data.summary, summarized: true }
            : it
        )
      );
    } catch (e) {
      console.error(e);
      alert("Error summarizing: " + (e.message || e));
    } finally {
      setLoadingId(null);
    }
  };

  const filteredItems = items.filter(
    (it) =>
      it.title.toLowerCase().includes(search.toLowerCase()) ||
      (it.summary_text || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="panel">
      <h2>Summarize Articles</h2>

      {/* 🔎 Search */}
      <div style={{ marginBottom: 10 }}>
        <input
          type="text"
          placeholder="Search news..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: "6px", width: "60%" }}
        />
      </div>

      <div className="news-list">
        {filteredItems.map((it) => (
          <div key={it.id} className="news-item">
            <a href={it.link} target="_blank" rel="noreferrer">
              {it.title}
            </a>
            <div className="meta">{it.published}</div>
            <div style={{ marginTop: 6 }}>
              <button onClick={() => doSummarize(it.id)} disabled={loadingId === it.id}>
                {it.summarized ? "Re-summarize" : "Summarize"}
              </button>
            </div>
            {it.summary_text && <blockquote>{it.summary_text}</blockquote>}
          </div>
        ))}
      </div>
    </div>
  );
}
