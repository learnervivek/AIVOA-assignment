import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { dismissMissingEvidence } from '../../store/slices/rcaSlice';
import {
  AlertTriangle,
  CheckCircle2,
  FileQuestion,
  Sparkles,
  X,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export const MissingEvidenceSection: React.FC = () => {
  const dispatch = useAppDispatch();
  const { rca_analysis } = useAppSelector((state) => state.rca);
  const missingEvidence = rca_analysis.missing_evidence || [];

  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  const handleDismiss = (index: number) => {
    dispatch(dismissMissingEvidence(index));
  };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-amber-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-amber-50/70 border-b border-amber-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <FileQuestion className="w-4 h-4 text-amber-700" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            2. Missing Evidence & Investigation Gaps
          </h3>
          <span className="text-[10px] font-bold text-amber-800 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded-full flex items-center space-x-1">
            <Sparkles className="w-2.5 h-2.5 text-amber-600" />
            <span>Senior QA Auditor Node</span>
          </span>
          <span className="text-[10px] font-bold text-slate-500 bg-white/80 border border-slate-200 px-2 py-0.5 rounded">
            {missingEvidence.length} {missingEvidence.length === 1 ? 'Gap' : 'Gaps'} Flagged
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-amber-800 hover:text-amber-950 font-semibold flex items-center space-x-1 px-2 py-1 rounded hover:bg-amber-100/50 transition-colors"
          >
            <span>{isExpanded ? 'Collapse' : 'Expand'}</span>
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="p-6">
          <p className="text-xs text-slate-600 mb-4 leading-relaxed">
            Per <strong className="font-semibold text-slate-800">ICH Q7 §12 (Laboratory Controls)</strong> &{' '}
            <strong className="font-semibold text-slate-800">ICH Q9 (Quality Risk Management)</strong>, every root cause hypothesis requires verifiable evidence. The AI Auditor cross-checks your deviation notes against standard technical requirements to detect missing records before QA closure.
          </p>

          {missingEvidence.length === 0 ? (
            <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-4 flex items-center space-x-3 text-emerald-800">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <div className="text-xs">
                <span className="font-bold">No Investigation Gaps Remaining.</span> All critical ICH Q7 documentation and technical records appear substantiated or verified by QA.
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {missingEvidence.map((item, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-amber-200 bg-amber-50/40 p-4 transition-all hover:bg-amber-50/70"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start space-x-3 flex-1">
                      <div className="mt-0.5 p-1 rounded-md bg-amber-100 text-amber-700 flex-shrink-0">
                        <AlertTriangle className="w-4 h-4" />
                      </div>
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center flex-wrap gap-2">
                          <h4 className="text-xs font-bold text-slate-900">{item.gap}</h4>
                          <span className="inline-flex items-center space-x-1 text-[10px] font-semibold text-amber-700 bg-amber-100 px-1.5 py-0.2 rounded">
                            <Sparkles className="w-2.5 h-2.5" />
                            <span>AI Identified</span>
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed">
                          <strong className="font-semibold text-slate-700">GMP Why It Matters: </strong>
                          {item.why_it_matters}
                        </p>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleDismiss(index)}
                      title="Mark as gathered or dismiss gap"
                      className="text-xs font-medium text-slate-500 hover:text-rose-700 hover:bg-rose-50 border border-slate-200 hover:border-rose-200 px-2 py-1 rounded flex items-center space-x-1 flex-shrink-0 transition-all"
                    >
                      <X className="w-3.5 h-3.5" />
                      <span>Dismiss / Verified</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
