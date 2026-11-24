import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { LeftSidebar } from './components/LeftSidebar';
import { DeviationOverviewSection } from './components/RCAForm/DeviationOverviewSection';
import { MissingEvidenceSection } from './components/RCAForm/MissingEvidenceSection';
import { RCAAnalysisSection } from './components/RCAForm/RCAAnalysisSection';
import { CAPASection } from './components/RCAForm/CAPASection';
import { AIAssistantPanel } from './components/AIAssistantPanel';
import { useAppDispatch, useAppSelector } from './store/hooks';
import { fetchInvestigationsThunk, saveInvestigationThunk, updateFormField, clearToast } from './store/slices/rcaSlice';
import {
  Save,
  CheckCircle2,
  RefreshCw,
  AlertCircle,
  ShieldCheck,
  X,
} from 'lucide-react';

export const App: React.FC = () => {
  const dispatch = useAppDispatch();
  const { form, saveStatus, errorMessage, toastMessage } = useAppSelector((state) => state.rca);

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);

  useEffect(() => {
    dispatch(fetchInvestigationsThunk());
  }, [dispatch]);

  // Auto-dismiss confirmation toast after 5 seconds
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => {
        dispatch(clearToast());
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [toastMessage, dispatch]);

  const handleSave = () => {
    dispatch(saveInvestigationThunk());
  };

  const handleQASignOff = () => {
    dispatch(updateFormField({ field: 'status', value: 'QA Approved' }));
    dispatch(saveInvestigationThunk());
  };

  const isCritical = form.severity === 'Critical';
  const isMajor = form.severity === 'Major';

  return (
    <div className="h-screen flex flex-col bg-slate-100 font-sans overflow-hidden">
      {/* Global Top Navbar */}
      <Navbar />

      {/* 3-Column Studio Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Column 1: Left Collapsible Investigations Sidebar */}
        <LeftSidebar
          collapsed={isSidebarCollapsed}
          onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />

        {/* Column 2: Center Main Workspace (Structured RCA Form ~65% width) */}
        <main className="flex-1 flex flex-col h-full overflow-hidden bg-slate-100">
          {/* Workspace Sticky Control Bar */}
          <div className="px-6 py-3.5 bg-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-4 flex-shrink-0 shadow-xs z-10">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <span className="font-mono text-sm font-bold text-slate-900 bg-slate-100 border border-slate-200 px-2.5 py-1 rounded-md">
                  {form.deviation_number || 'DEV-DRAFT'}
                </span>
                <span
                  className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                    isCritical
                      ? 'bg-rose-100 text-rose-800 border-rose-300'
                      : isMajor
                      ? 'bg-amber-100 text-amber-800 border-amber-300'
                      : 'bg-blue-100 text-blue-800 border-blue-300'
                  }`}
                >
                  {form.severity}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                    form.status === 'QA Approved'
                      ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                      : form.status === 'Under Review'
                      ? 'bg-purple-100 text-purple-800 border-purple-300'
                      : 'bg-slate-100 text-slate-700 border-slate-300'
                  }`}
                >
                  {form.status}
                </span>
              </div>

              <div className="hidden md:flex items-center space-x-2 text-xs text-slate-500">
                <span>•</span>
                <span className="font-semibold text-slate-700 truncate max-w-xs">
                  {form.api_product_name || 'Active API'}
                </span>
                <span>•</span>
                <span className="font-mono text-slate-600">{form.batch_lot_number || 'Batch Lot'}</span>
              </div>
            </div>

            {/* Action Buttons: Save & QA Sign-Off */}
            <div className="flex items-center space-x-2.5">
              {form.status !== 'QA Approved' && (
                <button
                  type="button"
                  onClick={handleQASignOff}
                  disabled={saveStatus === 'saving'}
                  className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-xs transition-all disabled:opacity-50"
                  title="Mark QA Approved and commit to PostgreSQL"
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>QA Sign-Off</span>
                </button>
              )}

              <button
                type="button"
                onClick={handleSave}
                disabled={saveStatus === 'saving'}
                className="flex items-center space-x-1.5 px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-xs transition-all disabled:opacity-50"
              >
                {saveStatus === 'saving' ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                    <span>Saving to DB...</span>
                  </>
                ) : saveStatus === 'saved' ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Saved (PostgreSQL)</span>
                  </>
                ) : saveStatus === 'error' ? (
                  <>
                    <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
                    <span>Save Failed</span>
                  </>
                ) : (
                  <>
                    <Save className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Save Investigation</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Form Scrollable Workspace Area */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
            {saveStatus === 'error' && errorMessage && (
              <div className="rounded-xl bg-rose-50 border border-rose-200 p-4 text-xs text-rose-800 flex items-center space-x-2 shadow-xs">
                <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                <span>
                  <strong>PostgreSQL Persistence Error:</strong> {errorMessage}
                </span>
              </div>
            )}

            {/* Form Section 1: Deviation & Batch Overview */}
            <DeviationOverviewSection />

            {/* Form Section 2: Missing Evidence & Investigation Gaps */}
            <MissingEvidenceSection />

            {/* Form Section 3: Root Cause Analysis (5 Whys & 6M Fishbone) */}
            <RCAAnalysisSection />

            {/* Form Section 4: CAPA Action Plan */}
            <CAPASection />

            <div className="py-4 text-center text-xs text-slate-400 border-t border-slate-200">
              ICH Q7 §12 & Q10 Quality Management System • Automated 21 CFR Part 11 Audit Trail
            </div>
          </div>
        </main>

        {/* Column 3: Right Persistent Panel (AI RCA Co-Pilot ~35% width) */}
        <aside className="w-[380px] lg:w-[440px] xl:w-[460px] flex-shrink-0 h-full shadow-lg z-20">
          <AIAssistantPanel />
        </aside>
      </div>

      {/* Floating 21 CFR Part 11 Confirmation Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center space-x-3 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-2xl border border-slate-700 animate-bounce">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span className="text-xs font-semibold">{toastMessage}</span>
          <button
            type="button"
            onClick={() => dispatch(clearToast())}
            className="text-slate-400 hover:text-white p-1 rounded transition-colors ml-2"
            title="Dismiss notification"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};
export default App;
