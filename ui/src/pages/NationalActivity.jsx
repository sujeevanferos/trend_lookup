import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, Activity, Calendar, Target } from 'lucide-react';
import clsx from 'clsx';

const API_PATH = window.location.origin.replace(':5173', ':8000');
const NATIONAL_INDICATORS_PATH = `${API_PATH}/output/national_activity_indicators.json`;

const NationalActivity = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(NATIONAL_INDICATORS_PATH);
                if (!response.ok) throw new Error('Failed to fetch national indicators');

                const jsonData = await response.json();
                setData(jsonData);
            } catch (err) {
                console.error("Fetch Error:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-10 text-center">Loading national indicators...</div>;
    if (error) return <div className="p-10 text-center text-red-500">Error: {error}</div>;

    const indicators = data?.indicators || [];
    const totalCount = data?.total_indicators || 0;

    return (
        <div className="space-y-6">
            {/* Header Stats */}
            <div className="bg-gradient-to-r from-purple-600 to-purple-800 dark:from-purple-800 dark:to-purple-900 p-8 rounded-2xl text-white shadow-lg">
                <div className="flex items-center gap-4 mb-4">
                    <div className="p-4 bg-white/20 rounded-xl">
                        <Activity size={32} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold">National Activity Indicators</h1>
                        <p className="text-purple-100">Major events, developments, disruptions, or topics gaining traction in the public space</p>
                    </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white/10 p-4 rounded-xl">
                        <p className="text-sm text-purple-100">Total Indicators</p>
                        <p className="text-4xl font-bold">{totalCount}</p>
                    </div>
                    <div className="bg-white/10 p-4 rounded-xl">
                        <p className="text-sm text-purple-100">Last Updated</p>
                        <p className="text-lg font-semibold">{data?.generated_at ? new Date(data.generated_at).toLocaleString() : 'N/A'}</p>
                    </div>
                    <div className="bg-white/10 p-4 rounded-xl">
                        <p className="text-sm text-purple-100">Coverage</p>
                        <p className="text-lg font-semibold">Real-time Monitoring</p>
                    </div>
                </div>
            </div>

            {/* Indicators List */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
                <h2 className="text-2xl font-bold mb-6 dark:text-white">Active National Indicators</h2>

                {indicators.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        <Activity size={48} className="mx-auto mb-4 opacity-50" />
                        <p>No national activity indicators detected at this time.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {indicators.map((indicator, index) => (
                            <div
                                key={indicator.id || index}
                                className="border border-gray-200 dark:border-gray-700 p-6 rounded-xl hover:shadow-lg transition-shadow"
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex-1">
                                        <h3 className="text-lg font-semibold dark:text-white mb-2">
                                            {indicator.headline}
                                        </h3>
                                        <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
                                            <span className="flex items-center gap-1">
                                                <Calendar size={14} />
                                                {new Date(indicator.timestamp).toLocaleString()}
                                            </span>
                                            <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full">
                                                {indicator.thematic_category}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="text-right">
                                        <div className={clsx(
                                            "text-2xl font-bold",
                                            indicator.impact_score > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                                        )}>
                                            {indicator.impact_score > 0 ? '+' : ''}{indicator.impact_score?.toFixed(3)}
                                        </div>
                                        <p className="text-xs text-gray-500">Impact Score</p>
                                    </div>
                                </div>

                                {indicator.top_industries_affected && indicator.top_industries_affected.length > 0 && (
                                    <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                                        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                            Top Affected Industries:
                                        </p>
                                        <div className="flex flex-wrap gap-2">
                                            {indicator.top_industries_affected.map((industry, idx) => (
                                                <span
                                                    key={idx}
                                                    className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm"
                                                >
                                                    {industry}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default NationalActivity;
