import React, { useMemo, useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function TopChart({ events }) {
  const [refreshKey, setRefreshKey] = useState(0);

  // Listen for global "reload chart" events
  useEffect(() => {
    const fn = () => setRefreshKey((v) => v + 1);
    window.addEventListener("evolvex:reload", fn);
    return () => window.removeEventListener("evolvex:reload", fn);
  }, []);

  // Aggregate industry impact
  const aggregated = useMemo(() => {
    const sums = {};
    const counts = {};

    (events || []).forEach((ev) => {
      Object.entries(ev.industry_impact || {}).forEach(([industry, score]) => {
        sums[industry] = (sums[industry] || 0) + score;
        counts[industry] = (counts[industry] || 0) + 1;
      });
    });

    const avg = Object.keys(sums).map((key) => ({
      key,
      value: +(sums[key] / counts[key]).toFixed(4),
    }));

    return avg.sort((a, b) => Math.abs(b.value) - Math.abs(a.value)).slice(0, 12);
  }, [events, refreshKey]);

  if (!aggregated.length) {
    return <div className="text-slate-400">No data available</div>;
  }

  const labels = aggregated.map((a) => a.key);
  const dataVals = aggregated.map((a) => a.value);

  const colors = dataVals.map((v) =>
    v >= 0 ? "rgba(16,185,129,0.9)" : "rgba(239,68,68,0.9)"
  );

  const data = {
    labels,
    datasets: [
      {
        label: "Average Impact",
        data: dataVals,
        backgroundColor: colors,
      },
    ],
  };

  return (
    <div style={{ height: "360px" }}>
      <Bar data={data} key={refreshKey} />
    </div>
  );
}

