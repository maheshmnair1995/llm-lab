import React, { useEffect, useState } from "react";
import { topics } from "../api";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

export default function Analytics() {
  const [data, setData] = useState(null);
  const [clusters, setClusters] = useState(5);

  const load = async () => {
    try {
      const r = await topics(clusters);
      setData(r.data);
    } catch (e) {
      console.error(e);
      setData(null);
    }
  };

  useEffect(() => {
    load();
  }, [clusters]);

  if (!data)
    return (
      <div className="panel">
        <h2>Analytics</h2>
        <p>Loading...</p>
      </div>
    );

  const pieLabels = data.topics.map((t) => `Topic ${t.cluster}`);
  const pieData = data.topics.map((t) => t.count);
  const barLabels = data.topics.map(
    (t) => `T${t.cluster}: ${t.top_terms.slice(0, 3).join(", ")}`
  );

  const colors = [
    "#4facfe",
    "#43e97b",
    "#f093fb",
    "#f5576c",
    "#30cfd0",
    "#ff9a9e",
    "#a18cd1",
    "#f6d365",
    "#5ee7df",
    "#c79081",
    "#c471ed",
    "#f7797d"
  ];

  return (
    <div className="panel">
      <h2>Analytics</h2>
      <div>
        <label>Clusters: </label>
        <input
          type="number"
          value={clusters}
          min={1}
          max={12}
          onChange={(e) => setClusters(Number(e.target.value))}
        />
        <button onClick={load} style={{ marginLeft: 8 }}>
          Refresh
        </button>
      </div>

      <div className="charts">
        <div className="chart">
          <h3>Topic distribution (pie)</h3>
          <Pie
            data={{
              labels: pieLabels,
              datasets: [
                {
                  data: pieData,
                  backgroundColor: colors.slice(0, pieData.length)
                }
              ]
            }}
          />
        </div>
        <div className="chart">
          <h3>Topics (bar)</h3>
          <Bar
            data={{
              labels: barLabels,
              datasets: [
                {
                  label: "Items",
                  data: pieData,
                  backgroundColor: colors.slice(0, pieData.length)
                }
              ]
            }}
          />
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <h4>Topic details</h4>
        {data.topics.map((t) => (
          <div
            key={t.cluster}
            style={{ border: "1px solid #ddd", padding: 8, marginBottom: 6 }}
          >
            <strong>
              Topic {t.cluster} — {t.count} items
            </strong>
            <div>Top terms: {t.top_terms.join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
