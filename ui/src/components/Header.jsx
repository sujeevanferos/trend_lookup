import React, { useEffect, useState } from "react";
import clsx from "clsx";

export default function Header({ tab, setTab, onRefresh, loading, lastLoaded }) {
  const [dark, setDark] = useState(() => localStorage.getItem("ui-dark") !== "0");

  // Load & persist dark mode
  useEffect(() => {
    if (dark) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
    localStorage.setItem("ui-dark", dark ? "1" : "0");
  }, [dark]);

  // Reload chart widgets (custom event)
  function reloadCharts() {
    window.dispatchEvent(new Event("evolvex:reload"));
    if (typeof onRefresh === "function") onRefresh();
  }

  return (
    <header className="flex items-center justify-between gap-6">
      {/* LEFT SIDE — Title & Subtitle */}
      <div>
        <h1 className="text-2xl font-semibold">evolveX — Industry Impact</h1>
        <p className="kicker mt-1">Real-time insights • Opportunity & Risk matrix</p>
      </div>

      {/* RIGHT SIDE — Controls */}
      <div className="flex items-center gap-4">
        
        {/* Tabs */}
        <div className="bg-slate-800/60 dark:bg-slate-700/60 rounded-lg p-1 flex shadow">
          <button
            onClick={() => setTab("home")}
            className={clsx(
              "px-4 py-2 rounded-md transition",
              tab === "home"
                ? "bg-sky-600 text-white shadow"
                : "text-slate-200/80 hover:bg-slate-700/40"
            )}
          >
            Home
          </button>

          <button
            onClick={() => setTab("history")}
            className={clsx(
              "px-4 py-2 rounded-md transition",
              tab === "history"
                ? "bg-sky-600 text-white shadow"
                : "text-slate-200/80 hover:bg-slate-700/40"
            )}
          >
            History
          </button>
        </div>

        {/* Manual refresh (fetch live_output.json) */}
        <button
          onClick={onRefresh}
          disabled={loading}
          className="px-3 py-2 rounded-md bg-slate-700/60 hover:bg-slate-600/60 transition disabled:opacity-50"
        >
          {loading ? "Loading…" : "Refresh"}
        </button>

        {/* Reload chart widgets */}
        <button
          onClick={reloadCharts}
          className="px-3 py-2 rounded-md bg-slate-700/60 hover:bg-slate-600/60 transition"
        >
          Reload Charts
        </button>

        {/* Dark mode toggle */}
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={dark}
            onChange={(e) => setDark(e.target.checked)}
          />
          <span className="text-sm text-slate-400">Dark</span>
        </label>

        {/* Last loaded time */}
        <span className="text-sm text-slate-400">
          {lastLoaded ? lastLoaded.toLocaleString() : "—"}
        </span>
      </div>
    </header>
  );
}

