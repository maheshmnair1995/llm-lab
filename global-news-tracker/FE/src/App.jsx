import React, { useState } from "react";
import FetchNews from "./components/FetchNews";
import Summarize from "./components/Summarize";
import Analytics from "./components/Analytics";

export default function App() {
  const [tab, setTab] = useState("fetch");
  return (
    <div className="app">
      <header className="header">
        <h1>Global News Topic Tracker</h1>
        <nav>
          <button onClick={() => setTab("fetch")} className={tab==="fetch"?"active":""}>Fetch News</button>
          <button onClick={() => setTab("summarize")} className={tab==="summarize"?"active":""}>Summarize</button>
          <button onClick={() => setTab("analytics")} className={tab==="analytics"?"active":""}>Analytics</button>
        </nav>
      </header>
      <main>
        {tab === "fetch" && <FetchNews/>}
        {tab === "summarize" && <Summarize/>}
        {tab === "analytics" && <Analytics/>}
      </main>
    </div>
  );
}
