import React, { useState, useEffect, useMemo } from 'react';
import { Search, ChevronDown, TrendingUp, TrendingDown, Calendar } from 'lucide-react';
import { HISTORY_JSONL_PATH } from '../config';
import { INDUSTRIES } from '../constants';
import clsx from 'clsx';
import dayjs from 'dayjs';

const Analysis = () => {
    const [rawData, setRawData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedIndustry, setSelectedIndustry] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(HISTORY_JSONL_PATH);
                if (!response.ok) throw new Error('Failed to fetch history');
                const text = await response.text();

                // Parse JSONL and flatten events
                const parsedData = text.trim().split('\n').flatMap(line => {
                    try {
                        const snapshot = JSON.parse(line);
                        if (!snapshot || !snapshot.events) return [];

                        return snapshot.events.flatMap(event => {
                            const baseEvent = {
                                ...event,
                                timestamp: event.timestamp || snapshot.run_timestamp
                            };

                            // Handle new multi-industry format
                            if (event.impacts && Array.isArray(event.impacts)) {
                                return event.impacts.map(impact => ({
                                    ...baseEvent,
                                    industry: impact.industry,
                                    score: impact.score,
                                    impact_type: impact.impact_type
                                }));
                            }

                            // Fallback for old format
                            return [{
                                ...baseEvent,
                                industry: event.category || 'General',
                                score: event.opportunity_score || 0
                            }];
                        });
                    } catch (e) {
                        return [];
                    }
                });

                setRawData(parsedData);
            } catch (err) {
                console.error(err);
                setRawData([]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Use strict industry list
    const industries = INDUSTRIES;

    // Set default selection
    useEffect(() => {
        if (!selectedIndustry && industries.length > 0) {
            setSelectedIndustry(industries[0]);
        }
    }, [industries, selectedIndustry]);

    // Filter data for chart
    const chartData = useMemo(() => {
        if (!selectedIndustry) return [];
        const filtered = rawData
            .filter(d => (d.industry || 'General') === selectedIndustry)
            .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

        // Aggregate by hour/time to avoid too many points
        // For simplicity, we'll take the last 50 points
        return filtered.slice(-50).map(d => ({
            time: dayjs(d.timestamp).format('HH:mm'),
            fullDate: dayjs(d.timestamp).format('MMM D, HH:mm'),
            score: parseFloat(d.score)
        }));
    }, [rawData, selectedIndustry]);

    // Get top news for selected industry
    const topNews = useMemo(() => {
        if (!selectedIndustry) return [];
        return rawData
            .filter(d => (d.industry || 'General') === selectedIndustry)
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)) // Newest first
            .slice(0, 5);
    }, [rawData, selectedIndustry]);

    const filteredIndustries = industries.filter(ind =>
        ind.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // SVG Chart Helper
    const renderChart = () => {
        if (chartData.length < 2) return <div className="flex items-center justify-center h-full text-gray-500">Not enough data for chart</div>;

        const width = 800;
        const height = 300;
        const padding = 40;

        const minScore = -1;
        const maxScore = 1;

        const xScale = (index) => padding + (index / (chartData.length - 1)) * (width - 2 * padding);
        const yScale = (score) => height - (padding + ((score - minScore) / (maxScore - minScore)) * (height - 2 * padding));

        const points = chartData.map((d, i) => `${xScale(i)},${yScale(d.score)}`).join(' ');
        const zeroLineY = yScale(0);

        return (
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
                {/* Grid Lines */}
                <line x1={padding} y1={padding} x2={width - padding} y2={padding} stroke="#374151" strokeOpacity="0.2" />
                <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#374151" strokeOpacity="0.2" />
                <line x1={padding} y1={zeroLineY} x2={width - padding} y2={zeroLineY} stroke="#9CA3AF" strokeWidth="1" strokeDasharray="4 4" />

                {/* Y Axis Labels */}
                <text x={padding - 10} y={yScale(1)} fill="#9CA3AF" fontSize="12" textAnchor="end" alignmentBaseline="middle">1.0</text>
                <text x={padding - 10} y={yScale(0)} fill="#9CA3AF" fontSize="12" textAnchor="end" alignmentBaseline="middle">0.0</text>
                <text x={padding - 10} y={yScale(-1)} fill="#9CA3AF" fontSize="12" textAnchor="end" alignmentBaseline="middle">-1.0</text>

                {/* Line */}
                <polyline points={points} fill="none" stroke="#3B82F6" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

                {/* Points */}
                {chartData.map((d, i) => (
                    <circle
                        key={i}
                        cx={xScale(i)}
                        cy={yScale(d.score)}
                        r="4"
                        fill="#3B82F6"
                        stroke="#fff"
                        strokeWidth="2"
                        className="hover:r-6 transition-all cursor-pointer"
                    >
                        <title>{`${d.fullDate}: ${d.score.toFixed(4)}`}</title>
                    </circle>
                ))}
            </svg>
        );
    };

    if (loading) return <div className="p-10 text-center">Loading history...</div>;

    return (
        <div className="flex flex-col md:flex-row gap-6 h-[calc(100vh-140px)]">
            {/* Left Sidebar (Industry List) */}
            <div className="w-full md:w-1/4 flex flex-col gap-4 bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm h-full overflow-hidden">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <input
                        type="text"
                        placeholder="Search industries..."
                        className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="flex-1 overflow-y-auto space-y-1 pr-2 custom-scrollbar">
                    {filteredIndustries.map(ind => (
                        <button
                            key={ind}
                            onClick={() => setSelectedIndustry(ind)}
                            className={clsx(
                                "w-full text-left px-4 py-3 rounded-xl transition-all flex items-center justify-between group",
                                selectedIndustry === ind
                                    ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30"
                                    : "hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-600 dark:text-gray-300"
                            )}
                        >
                            <span className="font-medium">{ind}</span>
                            {selectedIndustry === ind && <TrendingUp size={16} />}
                        </button>
                    ))}
                </div>
            </div>

            {/* Right Content (Chart & News) */}
            <div className="w-full md:w-3/4 flex flex-col gap-6 h-full overflow-y-auto pr-2">
                {/* Chart Section */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm min-h-[400px]">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400">
                                <TrendingUp size={20} />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold dark:text-white">{selectedIndustry}</h2>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Opportunity Score Trend</p>
                            </div>
                        </div>
                    </div>

                    <div className="h-[300px] w-full">
                        {renderChart()}
                    </div>
                </div>

                {/* Recent News Section */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex-1">
                    <h3 className="text-lg font-bold mb-4 dark:text-white flex items-center gap-2">
                        <Calendar size={18} className="text-gray-400" />
                        Recent News & Signals
                    </h3>
                    <div className="space-y-3">
                        {topNews.map((item, idx) => (
                            <div key={idx} className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900/50 border border-gray-100 dark:border-gray-700/50 hover:border-blue-500/30 transition-all group">
                                <div className="flex justify-between items-start gap-4">
                                    <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed group-hover:text-blue-400 transition-colors">
                                        {item.text}
                                    </p>
                                    <span className={clsx(
                                        "shrink-0 px-2 py-1 rounded text-xs font-bold",
                                        item.score > 0 ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                                    )}>
                                        {parseFloat(item.score).toFixed(2)}
                                    </span>
                                </div>
                                <div className="mt-2 flex items-center gap-2 text-xs text-gray-400">
                                    <span>{dayjs(item.timestamp).format('MMM D, HH:mm')}</span>
                                    <span>•</span>
                                    <span>Source: EvolveX AI</span>
                                </div>
                            </div>
                        ))}
                        {topNews.length === 0 && (
                            <p className="text-gray-500 text-center py-4">No news available for this period.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analysis;
