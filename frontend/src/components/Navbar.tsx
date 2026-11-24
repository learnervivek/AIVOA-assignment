import React, { useEffect, useState } from 'react';
import { Activity, ShieldCheck, Database, AlertCircle, Upload } from 'lucide-react';
import { checkSystemHealth } from '../services/api';
import { HealthResponse } from '../types';

interface NavbarProps {
  onOpenUpload?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenUpload }) => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    checkSystemHealth()
      .then((data) => {
        setHealth(data);
        setError(false);
      })
      .catch(() => {
        setError(true);
      });
  }, []);

  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-600 flex items-center justify-center font-bold text-white shadow-inner">
            <Activity className="w-6 h-6 text-cyan-100" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-lg tracking-tight text-white">
                PharmaRCA Intelligence
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider bg-cyan-950 text-cyan-400 border border-cyan-800 px-2 py-0.5 rounded">
                ICH Q7 / GMP
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Active Pharmaceutical Ingredient (API) Root Cause Analysis & CAPA Suite
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 sm:space-x-4">
          {onOpenUpload && (
            <button
              onClick={onOpenUpload}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-lg shadow-sm transition-all"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Ingest Document</span>
            </button>
          )}

          <div className="hidden lg:flex items-center space-x-2 text-xs bg-slate-800/80 border border-slate-700/60 rounded-full px-3 py-1.5 text-slate-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>21 CFR Part 11 Audit Trail Ready</span>
          </div>

          <div className="flex items-center space-x-2 text-xs bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5">
            <Database className="w-4 h-4 text-cyan-400" />
            {error ? (
              <span className="flex items-center text-rose-400 font-medium">
                <AlertCircle className="w-3.5 h-3.5 mr-1" /> DB Offline
              </span>
            ) : health ? (
              <span className="flex items-center text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-1.5"></span>
                PostgreSQL Connected ({health.database.database})
              </span>
            ) : (
              <span className="text-slate-400">Checking DB...</span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
