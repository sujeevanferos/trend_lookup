import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, AlertTriangle } from 'lucide-react';
import { LIVE_JSON_PATH } from '../config';
import clsx from 'clsx';

const Home = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(LIVE_JSON_PATH);
        if (!response.ok) throw new Error('Failed to fetch data');

        const jsonData = await response.json();
        const rawList = Array.isArray(jsonData) ? jsonData : (jsonData?.events || []);

        // Process data: Show only the HIGHEST-IMPACT industry per news item (avoids duplication)
        const processedData = rawList.map(item => {
          if (!item.impacts || item.impacts.length === 0) {
            return {
              text: item.text || 'No text',
              industry: 'Other',
              thematic_category: item.thematic_category || 'General',
              impact_type: 'Neutral',
              score: 0,
              relevance: 0
            };
          }

          // Find the impact with the highest absolute score
          const topImpact = item.impacts.reduce((prev, current) => {
            return Math.abs(current.score) > Math.abs(prev.score) ? current : prev;
          });

          return {
            text: item.text,
            industry: topImpact.industry,
            thematic_category: item.thematic_category || 'General',
            impact_type: topImpact.impact_type,
            score: topImpact.score,
            relevance: topImpact.relevance
          };
        });

        setData(processedData);
      } catch (err) {
        console.error("Fetch Error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-10 text-center">Loading dashboard...</div>;
  if (error) return <div className="p-10 text-center text-red-500">Error: {error}</div>;

  const safeData = Array.isArray(data) ? data : [];

  // Calculate stats with safety
  let avgScore = 0;
  let topOpp = { score: 0, industry: 'N/A', text: 'No data available' };
  let topRisk = { score: 0, industry: 'N/A', text: 'No data available' };
  let chartData = [];

  try {
    if (safeData.length > 0) {
      const totalScore = safeData.reduce((acc, item) => acc + (Number(item.score) || 0), 0);
      avgScore = totalScore / safeData.length;

      topOpp = safeData.reduce((prev, current) => {
        const prevScore = Number(prev.score) || -999;
        const currScore = Number(current.score) || -999;
        return prevScore > currScore ? prev : current;
      }, { score: -999 });
      if (topOpp.score === -999) topOpp = { score: 0, industry: 'N/A', text: 'No data' };

      topRisk = safeData.reduce((prev, current) => {
        const prevScore = Number(prev.score) || 999;
        const currScore = Number(current.score) || 999;
        return prevScore < currScore ? prev : current;
      }, { score: 999 });
      if (topRisk.score === 999) topRisk = { score: 0, industry: 'N/A', text: 'No data' };

      // Aggregate scores by industry for the chart
      const industryScores = {};
      safeData.forEach(item => {
        const ind = item.industry || 'Unknown';
        if (!industryScores[ind]) industryScores[ind] = 0;
        industryScores[ind] += Number(item.score) || 0;
      });

      chartData = Object.entries(industryScores)
        .map(([name, score]) => ({ name, score }))
        .sort((a, b) => Math.abs(b.score) - Math.abs(a.score))
        .slice(0, 10);
    }
  } catch (e) {
    console.error("Error calculating stats:", e);
  }

  return (
    <div className="space-y-6">
      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl text-blue-600 dark:text-blue-400">
              <Activity size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Market Sentiment</p>
              <h3 className="text-2xl font-bold dark:text-white">
                {avgScore > 0 ? 'Positive' : 'Negative'} ({avgScore.toFixed(2)})
              </h3>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl text-green-600 dark:text-green-400">
              <TrendingUp size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Top Opportunity</p>
              <h3 className="text-lg font-bold dark:text-white truncate w-48" title={topOpp.text}>
                {topOpp.industry || 'General'}
              </h3>
              <p className="text-xs text-green-500">Score: {topOpp.score?.toFixed(2)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-xl text-red-600 dark:text-red-400">
              <AlertTriangle size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Top Risk</p>
              <h3 className="text-lg font-bold dark:text-white truncate w-48" title={topRisk.text}>
                {topRisk.industry || 'General'}
              </h3>
              <p className="text-xs text-red-500">Score: {topRisk.score?.toFixed(2)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chart (Horizontal Implementation) */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <h2 className="text-xl font-bold mb-6 dark:text-white">Market Overview (By Industry)</h2>
        <div className="space-y-3">
          {chartData.map((item, index) => {
            // Scale: Assuming max score is around 1.0. We map 1.0 to 100% of the half-width.
            // So width% = abs(score) * 100.
            const widthPct = Math.min(Math.abs(item.score) * 100, 100);

            return (
              <div key={index} className="flex items-center gap-4">
                {/* Label */}
                <div className="w-32 text-sm text-gray-600 dark:text-gray-300 truncate text-right" title={item.name}>
                  {item.name}
                </div>

                {/* Chart Area */}
                <div className="flex-1 h-8 flex items-center relative">
                  {/* Center Line */}
                  <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300 dark:bg-gray-600 z-0"></div>

                  {/* Negative Bar (Right aligned in left half) */}
                  <div className="flex-1 flex justify-end pr-0.5 z-10">
                    {item.score < 0 && (
                      <div
                        className="h-4 bg-red-500 rounded-l-md transition-all duration-500"
                        style={{ width: `${widthPct}%` }}
                      />
                    )}
                  </div>

                  {/* Positive Bar (Left aligned in right half) */}
                  <div className="flex-1 flex justify-start pl-0.5 z-10">
                    {item.score > 0 && (
                      <div
                        className="h-4 bg-green-500 rounded-r-md transition-all duration-500"
                        style={{ width: `${widthPct}%` }}
                      />
                    )}
                  </div>
                </div>

                {/* Score Value */}
                <div className={clsx(
                  "w-12 text-sm font-bold text-right",
                  item.score > 0 ? "text-green-600 dark:text-green-400" :
                    item.score < 0 ? "text-red-600 dark:text-red-400" : "text-gray-400"
                )}>
                  {item.score.toFixed(2)}
                </div>
              </div>
            );
          })}
          {chartData.length === 0 && (
            <div className="w-full text-center text-gray-500">No data available for chart</div>
          )}
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold dark:text-white">Live Market Data</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-gray-50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400">
              <tr>
                <th className="px-6 py-4 font-medium">News Snippet</th>
                <th className="px-6 py-4 font-medium">Core Industry</th>
                <th className="px-6 py-4 font-medium">Thematic Category</th>
                <th className="px-6 py-4 font-medium">Impact Type</th>
                <th className="px-6 py-4 font-medium">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {data.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="px-6 py-4 text-gray-600 dark:text-gray-300 max-w-md truncate" title={item.text}>
                    {item.text}
                  </td>
                  <td className="px-6 py-4 font-medium dark:text-white">{item.industry}</td>
                  <td className="px-6 py-4 text-gray-500 dark:text-gray-400">{item.thematic_category}</td>
                  <td className="px-6 py-4">
                    <span className={clsx(
                      "px-3 py-1 rounded-full text-xs font-medium",
                      item.impact_type === 'Opportunity' ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" :
                        item.impact_type === 'Threat' ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                          "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400"
                    )}>
                      {item.impact_type}
                    </span>
                  </td>
                  <td className={clsx("px-6 py-4 font-bold", item.score > 0 ? "text-green-500" : "text-red-500")}>
                    {Number(item.score).toFixed(4)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Home;
