import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import {
  loadInvestigationThunk,
  resetForm,
  deleteInvestigationThunk,
} from '../store/slices/rcaSlice';
import {
  Plus,
  Search,
  FileText,
  ChevronLeft,
  ChevronRight,
  Trash2,
  CheckCircle2,
  Clock,
  Layers,
} from 'lucide-react';
import { SeverityLevel, InvestigationStatus } from '../types';

interface LeftSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({ collapsed, onToggle }) => {
  const dispatch = useAppDispatch();
  const { savedInvestigations, selectedInvestigationId, loading } = useAppSelector(
    (state) => state.rca
  );

  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredItems = savedInvestigations.filter((inv) => {
    const matchesSearch =
      inv.deviation_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.api_product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.batch_lot_number.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesSeverity = severityFilter === 'all' || inv.severity === severityFilter;
    const matchesStatus = statusFilter === 'all' || inv.status === statusFilter;

    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const getSeverityPill = (sev: SeverityLevel) => {
    switch (sev) {
      case 'Critical':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      case 'Major':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getStatusIcon = (status: InvestigationStatus) => {
    switch (status) {
      case 'QA Approved':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />;
      case 'Under Review':
        return <Clock className="w-3.5 h-3.5 text-purple-600" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this deviation record?')) {
      dispatch(deleteInvestigationThunk(id));
    }
  };

  if (collapsed) {
    return (
      <aside className="w-16 bg-white border-r border-slate-200 flex flex-col items-center py-4 space-y-4 flex-shrink-0 transition-all duration-300">
        <button
          onClick={onToggle}
          title="Expand investigations sidebar"
          className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
        >
          <ChevronRight className="w-5 h-5" />
        </button>

        <button
          onClick={() => dispatch(resetForm())}
          title="New Investigation"
          className="w-10 h-10 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white flex items-center justify-center shadow-sm transition-all"
        >
          <Plus className="w-5 h-5" />
        </button>

        <div className="w-8 border-b border-slate-200"></div>

        <div className="flex-1 overflow-y-auto space-y-2 w-full px-2">
          {savedInvestigations.map((inv) => (
            <button
              key={inv.id}
              onClick={() => dispatch(loadInvestigationThunk(inv.id))}
              title={`${inv.deviation_number}: ${inv.title}`}
              className={`w-full p-2 rounded-lg text-xs font-bold truncate flex items-center justify-center transition-all ${
                selectedInvestigationId === inv.id
                  ? 'bg-cyan-100 text-cyan-900 border border-cyan-300'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {inv.deviation_number.split('-')[2] || inv.deviation_number.slice(0, 4)}
            </button>
          ))}
        </div>
      </aside>
    );
  }

  return (
    <aside className="w-80 bg-white border-r border-slate-200 flex flex-col h-[calc(100vh-4rem)] flex-shrink-0 transition-all duration-300">
      {/* Top Header */}
      <div className="p-4 border-b border-slate-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-cyan-600" />
            <h2 className="text-sm font-bold text-slate-900">Investigations</h2>
            <span className="text-[10px] font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
              {savedInvestigations.length}
            </span>
          </div>
          <button
            onClick={onToggle}
            title="Collapse sidebar"
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>

        <button
          onClick={() => dispatch(resetForm())}
          className="w-full flex items-center justify-center space-x-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold py-2.5 px-3 rounded-lg shadow-sm transition-all"
        >
          <Plus className="w-4 h-4 text-cyan-400" />
          <span>New Investigation</span>
        </button>
      </div>

      {/* Search & Filters */}
      <div className="p-3 border-b border-slate-200 bg-slate-50/60 space-y-2">
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search deviation, API, lot..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-md placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          />
        </div>

        <div className="flex gap-2">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-1/2 text-[11px] font-medium bg-white border border-slate-200 rounded px-2 py-1 text-slate-700 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="all">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="Major">Major</option>
            <option value="Minor">Minor</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-1/2 text-[11px] font-medium bg-white border border-slate-200 rounded px-2 py-1 text-slate-700 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="all">All Statuses</option>
            <option value="Draft">Draft</option>
            <option value="Under Review">Under Review</option>
            <option value="QA Approved">QA Approved</option>
          </select>
        </div>
      </div>

      {/* Investigations List */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-100 p-2 space-y-1">
        {filteredItems.length === 0 ? (
          <div className="p-6 text-center text-slate-400 text-xs">
            {loading ? 'Loading records...' : 'No deviations match your filter.'}
          </div>
        ) : (
          filteredItems.map((inv) => {
            const isSelected = selectedInvestigationId === inv.id;
            return (
              <div
                key={inv.id}
                onClick={() => dispatch(loadInvestigationThunk(inv.id))}
                className={`p-3 rounded-lg cursor-pointer transition-all border ${
                  isSelected
                    ? 'bg-cyan-50/70 border-cyan-400 shadow-xs'
                    : 'bg-white border-transparent hover:border-slate-200 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-slate-900 text-xs tracking-tight">
                    {inv.deviation_number}
                  </span>
                  <div className="flex items-center space-x-1.5">
                    <span
                      className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.2 rounded border ${getSeverityPill(
                        inv.severity
                      )}`}
                    >
                      {inv.severity}
                    </span>
                    <button
                      onClick={(e) => handleDelete(e, inv.id)}
                      title="Delete record"
                      className="text-slate-300 hover:text-rose-600 p-0.5 rounded transition-colors"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <div className="text-xs font-medium text-slate-700 line-clamp-1 mb-1">
                  {inv.title}
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="truncate max-w-[140px] font-medium text-slate-500">
                    {inv.api_product_name}
                  </span>
                  <div className="flex items-center space-x-1">
                    {getStatusIcon(inv.status)}
                    <span className="text-[10px] text-slate-500 font-medium">{inv.status}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-200 text-center text-[10px] text-slate-400 bg-slate-50">
        ICH Q7 GMP Batch Audit Trail
      </div>
    </aside>
  );
};
