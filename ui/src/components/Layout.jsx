import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, LineChart, Moon, Sun, Menu, Activity, BarChart3, Shield } from 'lucide-react';
import clsx from 'clsx';

const Layout = ({ children }) => {
    const [isDarkMode, setIsDarkMode] = useState(true);
    const location = useLocation();

    useEffect(() => {
        if (isDarkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [isDarkMode]);

    const navItems = [
        { path: '/', label: 'Home', icon: LayoutDashboard },
        { path: '/analysis', label: 'Analysis', icon: LineChart },
        { path: '/national-activity', label: 'National Activity', icon: Activity },
        { path: '/operational-environment', label: 'Operational', icon: BarChart3 },
        { path: '/risk-opportunity', label: 'Risk & Opportunity', icon: Shield },
    ];

    return (
        <div className={clsx("min-h-screen transition-colors duration-300", isDarkMode ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900")}>
            {/* Top Navigation */}
            <nav className={clsx("border-b px-6 py-4 flex items-center justify-between sticky top-0 z-50 backdrop-blur-md",
                isDarkMode ? "bg-gray-900/80 border-gray-800" : "bg-white/80 border-gray-200")}>

                <div className="flex items-center gap-8">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                            <span className="font-bold text-white">E</span>
                        </div>
                        <span className="text-xl font-bold tracking-tight">EvolveX</span>
                    </div>

                    <div className="hidden md:flex items-center gap-1">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.path;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={clsx(
                                        "px-4 py-2 rounded-lg flex items-center gap-2 transition-all",
                                        isActive
                                            ? (isDarkMode ? "bg-gray-800 text-blue-400" : "bg-blue-50 text-blue-600")
                                            : (isDarkMode ? "text-gray-400 hover:text-white hover:bg-gray-800" : "text-gray-600 hover:text-gray-900 hover:bg-gray-100")
                                    )}
                                >
                                    <Icon size={18} />
                                    <span className="font-medium">{item.label}</span>
                                </Link>
                            );
                        })}
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsDarkMode(!isDarkMode)}
                        className={clsx(
                            "p-2 rounded-lg transition-colors",
                            isDarkMode ? "hover:bg-gray-800 text-gray-400 hover:text-white" : "hover:bg-gray-100 text-gray-600"
                        )}
                    >
                        {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
                    </button>

                    <button className="md:hidden p-2 rounded-lg hover:bg-gray-800">
                        <Menu size={20} />
                    </button>
                </div>
            </nav>

            {/* Main Content */}
            <main className="p-6 max-w-7xl mx-auto">
                {children}
            </main>
        </div>
    );
};

export default Layout;
