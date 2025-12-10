import React, { useState, useEffect } from 'react';
import { BarChart3, Calendar, Target, TrendingDown } from 'lucide-react';
import clsx from 'clsx';

const API_PATH = window.location.origin.replace(':5173', ':8000');
const OPERATIONAL_INDICATORS_PATH = `${API_PATH}/output/operational_environment_indicators.json`;

const OperationalEnvironment = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(OPERATIONAL_INDICATORS_PATH);
                if (!response.ok) throw new Error('Failed to fetch operational indicators');

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
        const interval = setInterval(fetchData, 60000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-10 text-center">Loading operational indicators...</div>;
    if (error) return <div className="p-10 text-center text-red-500">Error: {error}</div>;

    const indicators = data?.indicators || [];
    const totalCount = data?.total_indicators || 0;

    return (
        <div className="space-y-6">
            {/* Header Stats */}
            <div className="bg-gradient-to-r from-emerald-600 to-teal-700 dark:from-emerald-800 dark:to-teal-900 p-8 rounded-2xl text-white shadow-lg">
                <div className="flex items-center gap-4 mb-4">
                    <div className="p-4 bg-white/20 rounded-xl">
                        <BarChart3 size={32} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold">Operational Environment Indicators</h1>
                        <p className="text-emerald-100">Abstracted signals that reflect conditions which may affect business operations or customer behavior</p>
                    </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white/10 p-4 rounded-xl">
                        <p className="text-sm text-emerald-100">Total Signals</p>
                        <p className="text-4xl font-bold">{totalCount}</p>
                    </div>
                    <div className="bg-white/10 p-4 rounded-xl">
                        <p className="text-sm text-emerald-100">Last Updated</p>
                        <p className="text-lg font-semibold">{data?.generated_at ? new Date(data.generated_at).toLocaleString() : 'N/A'}</p>
                    </div>
                    <div className="bg-white/10 p-4 rounded-xl">
                        <p className="text-sm text-emerald-100">Monitoring</p>
                        <p className="text-lg font-semibold">Cross-Sector Impact</p>
                    </div>
                </div>
            </div>

            {/* Indicators List */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
                <h2 className="text-2xl font-bold mb-6 dark:text-white">Active Operational Signals</h2>

                {indicators.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        <BarChart3 size={48} className="mx-auto mb-4 opacity-50" />
                        <p>No operational environment indicators detected at this time.</p>
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
                                            {indicator.signal}
                                        </h3>
                                        <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
                                            <span className="flex items-center gap-1">
                                                <Calendar size={14} />
                                                {new Date(indicator.timestamp).toLocaleString()}
                                            </span>
                                            <span className="px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded-full">
                                                {indicator.thematic_category}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="text-right ml-4">
                                        <div className="flex items-center gap-2 mb-1">
                                            <Target size={20} className="text-emerald-600 dark:text-emerald-400" />
                                            <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                                                {indicator.affected_industries_count || 0}
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-500">Industries Affected</p>
                                    </div>
                                </div>

                                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                                    <div>
                                        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                            Impact Score:
                                        </p>
                                        <div className={clsx(
                                            "text-xl font-bold",
                                            indicator.overall_impact > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                                        )}>
                                            {indicator.overall_impact > 0 ? '+' : ''}{indicator.overall_impact?.toFixed(3) || 'N/A'}
                                        </div>
                                    </div>

                                    {indicator.top_affected_industries && indicator.top_affected_industries.length > 0 && (
                                        <div>
                                            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                                Primary Sectors:
                                            </p>
                                            <div className="flex flex-wrap gap-2">
                                                {indicator.top_affected_industries.slice(0, 3).map((industry, idx) => (
                                                    <span
                                                        key={idx}
                                                        className="px-2 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 rounded-md text-xs"
                                                    >
                                                        {industry}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default OperationalEnvironment;
