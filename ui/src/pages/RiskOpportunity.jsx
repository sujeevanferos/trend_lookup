import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, Calendar, Shield, DollarSign } from 'lucide-react';
import clsx from 'clsx';

const API_PATH = window.location.origin.replace(':5173', ':8000');
const RISK_OPP_PATH = `${API_PATH}/output/risk_opportunity_insights.json`;

const RiskOpportunity = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all'); // all, risks, opportunities

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(RISK_OPP_PATH);
                if (!response.ok) throw new Error('Failed to fetch risk/opportunity insights');

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

    if (loading) return <div className="p-10 text-center">Loading risk/opportunity insights...</div>;
    if (error) return <div className="p-10 text-center text-red-500">Error: {error}</div>;

    const insights = data?.insights || [];
    const totalCount = data?.total_insights || 0;

    // Filter insights
    const filteredInsights = insights.filter(insight => {
        if (filter === 'risks') return insight.risk_score > 0.1;
        if (filter === 'opportunities') return insight.opportunity_score > 0.1;
        return true;
    });

    // Calculate stats
    const highRisks = insights.filter(i => i.risk_category === 'High Risk').length;
    const highOpps = insights.filter(i => i.opportunity_category === 'High Opportunity').length;

    return (
        <div className="space-y-6">
            {/* Header Stats */}
            <div className="bg-gradient-to-r from-indigo-600 to-blue-700 dark:from-indigo-800 dark:to-blue-900 p-8 rounded-2xl text-white shadow-lg">
                <div className="flex items-center gap-4 mb-4">
                    <div className="p-4 bg-white/20 rounded-xl">
                        <Shield size={32} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold">Risk & Opportunity Insights</h1>
                        <p className="text-indigo-100">Early warnings or emerging positive trends inferred from aggregated, real-time data</p>
                    </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white/10 p-4 rounded-xl">
                        <p className="text-sm text-indigo-100">Total Insights</p>
                        <p className="text-4xl font-bold">{totalCount}</p>
                    </div>
                    <div className="bg-white/10 p-4 rounded-xl">
                        <div className="flex items-center gap-2 mb-1">
                            <AlertTriangle size={20} />
                            <p className="text-sm text-indigo-100">High Risks</p>
                        </div>
                        <p className="text-3xl font-bold">{highRisks}</p>
                    </div>
                    <div className="bg-white/10 p-4 rounded-xl">
                        <div className="flex items-center gap-2 mb-1">
                            <TrendingUp size={20} />
                            <p className="text-sm text-indigo-100">High Opportunities</p>
                        </div>
                        <p className="text-3xl font-bold">{highOpps}</p>
                    </div>
                    <div className="bg-white/10 p-4 rounded-xl">
                        <p className="text-sm text-indigo-100">Last Updated</p>
                        <p className="text-lg font-semibold">{data?.generated_at ? new Date(data.generated_at).toLocaleString() : 'N/A'}</p>
                    </div>
                </div>
            </div>

            {/* Filter Tabs */}
            <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 flex gap-2">
                <button
                    onClick={() => setFilter('all')}
                    className={clsx(
                        'px-6 py-2 rounded-lg font-semibold transition-colors',
                        filter === 'all'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    )}
                >
                    All Insights ({totalCount})
                </button>
                <button
                    onClick={() => setFilter('risks')}
                    className={clsx(
                        'px-6 py-2 rounded-lg font-semibold transition-colors',
                        filter === 'risks'
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    )}
                >
                    Risks ({insights.filter(i => i.risk_score > 0.1).length})
                </button>
                <button
                    onClick={() => setFilter('opportunities')}
                    className={clsx(
                        'px-6 py-2 rounded-lg font-semibold transition-colors',
                        filter === 'opportunities'
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    )}
                >
                    Opportunities ({insights.filter(i => i.opportunity_score > 0.1).length})
                </button>
            </div>

            {/* Insights List */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
                {filteredInsights.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        <Shield size={48} className="mx-auto mb-4 opacity-50" />
                        <p>No insights match the current filter.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {filteredInsights.map((insight, index) => (
                            <div
                                key={insight.id || index}
                                className="border border-gray-200 dark:border-gray-700 p-6 rounded-xl hover:shadow-lg transition-shadow"
                            >
                                {/* Header */}
                                <div className="mb-4">
                                    <h3 className="text-lg font-semibold dark:text-white mb-2">
                                        {insight.headline}
                                    </h3>
                                    <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
                                        <span className="flex items-center gap-1">
                                            <Calendar size={14} />
                                            {new Date(insight.timestamp).toLocaleString()}
                                        </span>
                                        <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full">
                                            {insight.thematic_category}
                                        </span>
                                    </div>
                                </div>

                                {/* Risk & Opportunity Cards */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {/* Risk Card */}
                                    <div className="border-l-4 border-red-500 bg-red-50 dark:bg-red-900/20 p-4 rounded-r-lg">
                                        <div className="flex items-center gap-2 mb-2">
                                            <AlertTriangle size={20} className="text-red-600 dark:text-red-400" />
                                            <span className="font-bold text-lg text-red-700 dark:text-red-300">
                                                {insight.risk_category}
                                            </span>
                                        </div>
                                        <p className="text-3xl font-bold text-red-600 dark:text-red-400 mb-2">
                                            {insight.risk_score?.toFixed(3)}
                                        </p>
                                        <p className="text-sm text-gray-700 dark:text-gray-300">
                                            {insight.risk_explanation}
                                        </p>
                                    </div>

                                    {/* Opportunity Card */}
                                    <div className="border-l-4 border-green-500 bg-green-50 dark:bg-green-900/20 p-4 rounded-r-lg">
                                        <div className="flex items-center gap-2 mb-2">
                                            <DollarSign size={20} className="text-green-600 dark:text-green-400" />
                                            <span className="font-bold text-lg text-green-700 dark:text-green-300">
                                                {insight.opportunity_category}
                                            </span>
                                        </div>
                                        <p className="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">
                                            {insight.opportunity_score?.toFixed(3)}
                                        </p>
                                        <p className="text-sm text-gray-700 dark:text-gray-300">
                                            {insight.opportunity_explanation}
                                        </p>
                                    </div>
                                </div>

                                {/* Affected Industries */}
                                {insight.top_affected_industries && insight.top_affected_industries.length > 0 && (
                                    <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                                        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                            Top Affected Industries:
                                        </p>
                                        <div className="flex flex-wrap gap-2">
                                            {insight.top_affected_industries.map((industry, idx) => (
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

export default RiskOpportunity;
