import React from "react";
import dayjs from "dayjs";

// Score → color gradient generator
function scoreStyle(score) {
  if (score <= -0.7) return { background: "#7f1d1d", color: "#fff" }; // strong red
  if (score >= 0.7) return { background: "#065f46", color: "#fff" }; // strong green

  const pct = (score + 1) / 2; // normalize: [-1,1] → [0,1]

  // Dynamic gradient between red -> green
  const r = Math.round(200 - pct * 150);
  const g = Math.round(80 + pct * 150);

  return {
    background: `linear-gradient(90deg, rgba(${r},80,80,0.95), rgba(80,${g},80,0.95))`,
    color: "#fff",
  };
}

export default function EventsTable({ events }) {
  if (!events || !events.length) {
    return <div className="text-slate-400">No events available.</div>;
  }

  // Process rows
  const rows = events
    .map((e) => {
      const topIndustries = Object.entries(e.industry_impact || {})
        .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
        .slice(0, 2)
        .map(([ind, val]) => `${ind} (${val.toFixed(3)})`)
        .join(", ");

      return {
        id: e.id,
        time: e.timestamp,
        industry: topIndustries || "-",
        text: e.text,
        score: e.opportunity_score,
      };
    })
    .sort((a, b) => Math.abs(b.score) - Math.abs(a.score));

  return (
    <div className="overflow-x-auto">
      <table className="w-full table-auto text-sm">
        <thead className="text-slate-400">
          <tr>
            <th className="p-2 text-left">Date & Time</th>
            <th className="p-2 text-left">Industry Categories</th>
            <th className="p-2 text-left">Related News</th>
            <th className="p-2 text-left">Opportunity Score</th>
          </tr>
        </thead>

        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t border-slate-700">
              <td className="p-2">{dayjs(r.time).format("YYYY-MM-DD HH:mm")}</td>

              <td className="p-2">{r.industry}</td>

              <td className="p-2">
                {r.text.length > 150 ? r.text.slice(0, 150) + "…" : r.text}
              </td>

              <td className="p-2">
                <span className="px-3 py-1 rounded" style={scoreStyle(r.score)}>
                  {r.score.toFixed(3)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

