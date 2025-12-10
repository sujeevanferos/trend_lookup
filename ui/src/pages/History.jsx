import React, { useEffect, useMemo, useState } from "react";
import { HISTORY_JSONL_PATH } from "../config";
import { Line } from "react-chartjs-2";

import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

export default function History() {
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndustry, setSelectedIndustry] = useState("");
  const [rangeLimit, setRangeLimit] = useState(48);

  // Load history JSONL
  const loadHistory = async () => {
    setLoading(true);
    try {
      const res = await fetch(HISTORY_JSONL_PATH + "?t=" + Date.now());
      const text = await res.text();
      const lines = text.trim().split("\n").filter(Boolean);
      const parsed = lines.map((line) => JSON.parse(line));
      setSnapshots(parsed);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // allow charts to reload on demand
  useEffect(() => {
    const listener = () => loadHistory();
    window.addEventListener("evolvex:reload", listener);
    return () => window.removeEventListener("evolvex:reload", listener);
  }, []);

  // Extract all industries that appear anywhere
  const industries = useMemo(() => {
    const set = new Set();
    snapshots.forEach((snap) =>
      (snap.events || []).forEach((ev) =>
        Object.keys(ev.industry_impact || {}).forEach((ind) => set.add(ind))
      )
    );
    return Array.from(set).sort();
  }, [snapshots]);

  // Build time-series data
  const timeseries = useMemo(() => {
    if (!selectedIndustry) return [];
    const sliced = snapshots.slice(-rangeLimit);

    return sliced.map((snap) => {
      const values = (snap.events || [])
        .map((ev) => (ev.industry_impact || {})[selectedIndustry])
        .filter((v) => typeof v === "number");

      const avg = values.length ? values.reduce((a, b) => a + b) / values.length : 0;
      return { ts: snap.run_timestamp, value: +avg.toFixed(4) };
    });
  }, [snapshots, selectedIndustry, rangeLimit]);

  const chartData = {
    labels: timeseries.map((t) => new Date(t.ts).toLocaleString()),
    datasets: [
      {
        label: selectedIndustry,
        data: timeseries.map((t) => t.value),
        borderColor: "rgba(56,189,248,0.95)",
        backgroundColor: "rgba(56,189,248,0.15)",
        tension: 0.25,
        pointRadius: 2,
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* FILTER BAR */}
      <div className="card rounded-2xl p-4 shadow-lg">
        <h2 className="text-lg font-semibold">Historical Trends</h2>

        <div className="mt-3 flex flex-wrap items-center gap-3">
          {/* Industry Selector */}
          <select
            value={selectedIndustry}
            onChange={(e) => setSelectedIndustry(e.target.value)}
            className="p-2 rounded bg-slate-700/40"
          >
            <option value="">— Select Industry —</option>
            {industries.map((ind) => (
              <option key={ind} value={ind}>
                {ind}
              </option>
            ))}
          </select>

          {/* Range Selector */}
          <label className="text-sm text-slate-400">Range</label>
          <select
            value={rangeLimit}
            onChange={(e) => setRangeLimit(Number(e.target.value))}
            className="p-2 rounded bg-slate-700/40"
          >
            <option value={24}>Last 24</option>
            <option value={48}>Last 48</option>
            <option value={168}>Last Week</option>
            <option value={720}>Last Month</option>
          </select>
        </div>
      </div>

      {/* CHART */}
      <div className="card rounded-2xl p-4 shadow-lg">
        {loading && <div>Loading…</div>}
        {!loading && !selectedIndustry && (
          <div className="text-slate-400">Choose an industry to view its trend.</div>
        )}
        {!loading && selectedIndustry && <Line data={chartData} />}
      </div>
    </div>
  );
}

