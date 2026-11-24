import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import {
  setMethodology,
  updateWhyItem,
  addWhyItem,
  removeWhyItem,
  toggleRootCauseQA,
  updateRootCause,
  addFishboneFactor,
  updateFishboneFactor,
  removeFishboneFactor,
} from '../../store/slices/rcaSlice';
import { refineRCAThunk } from '../../store/slices/aiPanelSlice';
import {
  GitMerge,
  HelpCircle,
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  UserCheck,
  Cpu,
  Package,
  FileCode,
  Gauge,
  Thermometer,
  ShieldCheck,
  ShieldAlert,
  Layers,
  Edit2,
  Check,
  X,
} from 'lucide-react';
import { WhyItem, PotentialRootCause, Fishbone6M } from '../../types';

export const RCAAnalysisSection: React.FC = () => {
  const dispatch = useAppDispatch();
  const { rca_analysis } = useAppSelector((state) => state.rca);
  const activeTab = rca_analysis.methodology === '5_whys' ? '5_whys' : 'fishbone';

  // State for adding new factor per 6M category
  const [newFactors, setNewFactors] = useState<{ [key in keyof Fishbone6M]?: string }>({});
  // State for inline editing a fishbone factor: { category, index }
  const [editingFactor, setEditingFactor] = useState<{
    category: keyof Fishbone6M;
    index: number;
    text: string;
  } | null>(null);

  const fishbone = rca_analysis.fishbone_6m_data || {
    man: [],
    machine: [],
    material: [],
    method: [],
    measurement: [],
    environment: [],
  };

  const fiveWhys = rca_analysis.five_whys_data || [];
  const rootCauses = rca_analysis.potential_root_causes || [];

  const handleTabChange = (tab: 'fishbone' | '5_whys') => {
    dispatch(setMethodology(tab));
  };

  const handleWhyChange = (index: number, field: 'why' | 'answer', value: string) => {
    dispatch(updateWhyItem({ index, [field]: value }));
  };

  const handleDeepenWhyStep = (level: number, item: WhyItem) => {
    const prompt = `Dig deeper into Why #${level}: Question "${item.why || ''}" with Answer "${item.answer || ''}". Analyze lower-level physical, equipment calibration, and systemic failure mechanisms grounded in the deviation notes.`;
    dispatch(refineRCAThunk(prompt));
  };

  const handleAddFactor = (category: keyof Fishbone6M) => {
    const factor = newFactors[category];
    if (!factor || !factor.trim()) return;
    dispatch(addFishboneFactor({ category, factor: factor.trim() }));
    setNewFactors({ ...newFactors, [category]: '' });
  };

  const handleSaveFactorEdit = () => {
    if (!editingFactor) return;
    dispatch(
      updateFishboneFactor({
        category: editingFactor.category,
        index: editingFactor.index,
        factor: editingFactor.text,
      })
    );
    setEditingFactor(null);
  };

  const fishboneCategories: {
    key: keyof Fishbone6M;
    title: string;
    icon: React.ReactNode;
    items: string[];
    bgColor: string;
    borderColor: string;
  }[] = [
    {
      key: 'man',
      title: 'Man (Personnel / Training)',
      icon: <UserCheck className="w-4 h-4 text-blue-600" />,
      items: fishbone.man || [],
      bgColor: 'bg-blue-50/40',
      borderColor: 'border-blue-200',
    },
    {
      key: 'machine',
      title: 'Machine (Equipment / Utilities)',
      icon: <Cpu className="w-4 h-4 text-purple-600" />,
      items: fishbone.machine || [],
      bgColor: 'bg-purple-50/40',
      borderColor: 'border-purple-200',
    },
    {
      key: 'material',
      title: 'Material (APIs / Solvents / Lots)',
      icon: <Package className="w-4 h-4 text-amber-600" />,
      items: fishbone.material || [],
      bgColor: 'bg-amber-50/40',
      borderColor: 'border-amber-200',
    },
    {
      key: 'method',
      title: 'Method (SOPs / BMR / Protocols)',
      icon: <FileCode className="w-4 h-4 text-indigo-600" />,
      items: fishbone.method || [],
      bgColor: 'bg-indigo-50/40',
      borderColor: 'border-indigo-200',
    },
    {
      key: 'measurement',
      title: 'Measurement (Assay / Sensors)',
      icon: <Gauge className="w-4 h-4 text-cyan-600" />,
      items: fishbone.measurement || [],
      bgColor: 'bg-cyan-50/40',
      borderColor: 'border-cyan-200',
    },
    {
      key: 'environment',
      title: 'Environment (HVAC / Cleanroom)',
      icon: <Thermometer className="w-4 h-4 text-emerald-600" />,
      items: fishbone.environment || [],
      bgColor: 'bg-emerald-50/40',
      borderColor: 'border-emerald-200',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
      {/* Section Header */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <GitMerge className="w-4 h-4 text-indigo-700" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            3. Root Cause Analysis (RCA)
          </h3>
          <span className="text-[10px] font-bold text-slate-500 bg-slate-200/70 px-2 py-0.5 rounded">
            5 Whys & 6M Ishikawa
          </span>
        </div>

        {/* Methodology Toggle Tabs */}
        <div className="flex bg-slate-200/70 p-0.5 rounded-lg text-xs font-semibold">
          <button
            type="button"
            onClick={() => handleTabChange('fishbone')}
            className={`px-3 py-1 rounded-md transition-all flex items-center space-x-1.5 ${
              activeTab === 'fishbone'
                ? 'bg-white text-indigo-900 shadow-xs font-bold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Ishikawa 6M Fishbone</span>
          </button>
          <button
            type="button"
            onClick={() => handleTabChange('5_whys')}
            className={`px-3 py-1 rounded-md transition-all flex items-center space-x-1.5 ${
              activeTab === '5_whys'
                ? 'bg-white text-indigo-900 shadow-xs font-bold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>5 Whys Causal Stepper</span>
          </button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Mandatory GMP Regulatory Compliance Notice */}
        <div className="bg-amber-50/70 border border-amber-300 rounded-xl p-4 flex items-start space-x-3 text-amber-950">
          <ShieldAlert className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <div className="flex items-center space-x-2">
              <span className="font-bold uppercase tracking-wider text-amber-900">
                GMP / ICH Q7 Compliance Notice
              </span>
              <span className="text-[10px] bg-amber-200/80 text-amber-900 font-semibold px-1.5 py-0.2 rounded">
                Mandatory Review
              </span>
            </div>
            <p className="text-amber-800 leading-relaxed">
              <strong>AI-generated root causes are suggestions only until verified against evidence by a qualified person.</strong>{' '}
              Before investigation sign-off, a qualified QA Investigator must substantiate each identified cause with calibrated instrumentation, physical inspection, or analytical batch records.
            </p>
          </div>
        </div>

        {/* Tab 1: Ishikawa 6M Fishbone (Editable Grid) */}
        {activeTab === 'fishbone' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <p>
                Structured breakdown across the 6 GMP manufacturing dimensions. Click any factor to edit, or add custom contributing causes.
              </p>
              <span className="text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded">
                6M Ishikawa Model
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {fishboneCategories.map((cat) => (
                <div
                  key={cat.key}
                  className={`rounded-xl border ${cat.borderColor} ${cat.bgColor} p-4 transition-all flex flex-col justify-between shadow-xs`}
                >
                  <div>
                    {/* Category Title Bar */}
                    <div className="flex items-center justify-between pb-2 border-b border-slate-200/80 mb-3">
                      <div className="flex items-center space-x-2">
                        {cat.icon}
                        <h4 className="text-xs font-bold text-slate-800">{cat.title}</h4>
                      </div>
                      <span className="text-[10px] font-bold text-slate-600 bg-white px-2 py-0.5 rounded-full border border-slate-200">
                        {cat.items.length}
                      </span>
                    </div>

                    {/* Contributing Factor Items */}
                    {cat.items.length === 0 ? (
                      <p className="text-[11px] text-slate-400 italic py-2">
                        No factors entered. Add a factor below or run AI analysis.
                      </p>
                    ) : (
                      <ul className="space-y-2 mb-3">
                        {cat.items.map((item, idx) => {
                          const isEditing =
                            editingFactor?.category === cat.key && editingFactor?.index === idx;

                          if (isEditing) {
                            return (
                              <li
                                key={idx}
                                className="flex items-center space-x-1.5 bg-white p-1.5 rounded-lg border border-indigo-400 shadow-xs"
                              >
                                <input
                                  type="text"
                                  value={editingFactor.text}
                                  onChange={(e) =>
                                    setEditingFactor({ ...editingFactor, text: e.target.value })
                                  }
                                  className="flex-1 text-xs px-2 py-1 border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-500"
                                  autoFocus
                                  onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleSaveFactorEdit();
                                    if (e.key === 'Escape') setEditingFactor(null);
                                  }}
                                />
                                <button
                                  type="button"
                                  onClick={handleSaveFactorEdit}
                                  className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
                                  title="Save edit"
                                >
                                  <Check className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setEditingFactor(null)}
                                  className="p-1 text-slate-400 hover:bg-slate-100 rounded"
                                  title="Cancel"
                                >
                                  <X className="w-3.5 h-3.5" />
                                </button>
                              </li>
                            );
                          }

                          return (
                            <li
                              key={idx}
                              className="group text-xs text-slate-700 bg-white/90 rounded-lg px-2.5 py-1.5 border border-slate-200/80 leading-snug flex items-center justify-between gap-2 shadow-xs hover:border-indigo-300 transition-all"
                            >
                              <span className="flex-1 select-none">{item}</span>
                              <div className="flex items-center space-x-1 opacity-60 group-hover:opacity-100 transition-opacity">
                                <button
                                  type="button"
                                  onClick={() =>
                                    setEditingFactor({ category: cat.key, index: idx, text: item })
                                  }
                                  className="p-1 text-slate-400 hover:text-indigo-600 rounded"
                                  title="Edit factor"
                                >
                                  <Edit2 className="w-3 h-3" />
                                </button>
                                <button
                                  type="button"
                                  onClick={() =>
                                    dispatch(removeFishboneFactor({ category: cat.key, index: idx }))
                                  }
                                  className="p-1 text-slate-400 hover:text-rose-600 rounded"
                                  title="Delete factor"
                                >
                                  <Trash2 className="w-3 h-3" />
                                </button>
                              </div>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>

                  {/* Add Factor Input Bar */}
                  <div className="pt-2 border-t border-slate-200/60 mt-2">
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        handleAddFactor(cat.key);
                      }}
                      className="flex items-center space-x-1.5"
                    >
                      <input
                        type="text"
                        value={newFactors[cat.key] || ''}
                        onChange={(e) =>
                          setNewFactors({ ...newFactors, [cat.key]: e.target.value })
                        }
                        placeholder={`+ Add ${cat.key} factor...`}
                        className="flex-1 text-[11px] px-2.5 py-1 border border-slate-300 rounded bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder:text-slate-400"
                      />
                      <button
                        type="submit"
                        disabled={!newFactors[cat.key]?.trim()}
                        className="px-2 py-1 bg-white hover:bg-slate-100 text-slate-700 font-semibold text-[11px] border border-slate-300 rounded shadow-xs disabled:opacity-40"
                      >
                        Add
                      </button>
                    </form>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 2: 5 Whys Vertical Connected Stepper */}
        {activeTab === '5_whys' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <p>
                Vertical connected causal stepper. Edit questions & answers directly, add or remove levels, or ask AI to drill deeper into any step.
              </p>
              <button
                type="button"
                onClick={() => dispatch(addWhyItem())}
                className="text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-lg shadow-xs flex items-center space-x-1.5 transition-all"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Why Level</span>
              </button>
            </div>

            {fiveWhys.length === 0 ? (
              <div className="text-center py-10 border-2 border-dashed border-slate-200 rounded-xl text-slate-400">
                <HelpCircle className="w-10 h-10 mx-auto text-slate-300 mb-2" />
                <p className="text-xs font-semibold text-slate-600">No 5 Whys sequence entered yet.</p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Click "Analyze & Auto-Populate Form" in the AI Co-Pilot panel or click "Add Why Level".
                </p>
              </div>
            ) : (
              <div className="relative pl-6 space-y-6 before:absolute before:left-3 before:top-4 before:bottom-4 before:w-0.5 before:bg-indigo-200">
                {fiveWhys.map((item: WhyItem, idx: number) => (
                  <div key={idx} className="relative group">
                    {/* Connected Circle Node */}
                    <div className="absolute -left-6 top-4 w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center ring-4 ring-white shadow-sm z-10">
                      {item.level || idx + 1}
                    </div>

                    {/* Step Card */}
                    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-xs transition-all hover:border-indigo-300 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                            Level #{item.level || idx + 1} Causal Step
                          </span>
                        </div>

                        <div className="flex items-center space-x-2">
                          {/* Ask AI to Deepen Step button */}
                          <button
                            type="button"
                            onClick={() => handleDeepenWhyStep(item.level || idx + 1, item)}
                            title="Ask AI to drill deeper into physical and systemic mechanisms for this step"
                            className="text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-2.5 py-1 rounded-md flex items-center space-x-1.5 transition-colors"
                          >
                            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                            <span>Ask AI to Deepen Step</span>
                          </button>

                          {/* Delete Step */}
                          <button
                            type="button"
                            onClick={() => dispatch(removeWhyItem(idx))}
                            title="Remove this why step"
                            className="text-slate-400 hover:text-rose-600 p-1 rounded transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Direct Inline Edit Question & Answer */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                        <div>
                          <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                            Why Question / Failure Trigger
                          </label>
                          <input
                            type="text"
                            value={item.why}
                            onChange={(e) => handleWhyChange(idx, 'why', e.target.value)}
                            placeholder="e.g. Why did temperature probe TT-201 spike to 92°C?"
                            className="w-full text-xs font-semibold px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-slate-50/30"
                          />
                        </div>

                        <div>
                          <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                            Technical Explanation / Physical Mechanism
                          </label>
                          <textarea
                            rows={2}
                            value={item.answer}
                            onChange={(e) => handleWhyChange(idx, 'answer', e.target.value)}
                            placeholder="e.g. Steam regulator valve diaphragm ruptured due to thermal fatigue..."
                            className="w-full text-xs px-3 py-1.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-slate-50/30 leading-relaxed"
                          ></textarea>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Section 3.3: Potential Root Causes with Mandatory QA Confirmation */}
        <div className="pt-6 border-t border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                Identified Potential Root Causes & Hypotheses
              </h4>
              <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                {rootCauses.length} Records
              </span>
            </div>
            <span className="text-[11px] text-amber-800 font-semibold flex items-center space-x-1">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
              <span>QA Verification Required for Investigation Closeout</span>
            </span>
          </div>

          {rootCauses.length === 0 ? (
            <div className="rounded-xl bg-slate-50 border border-slate-200 p-8 text-center text-slate-400 text-xs">
              No potential root causes formulated yet. Run AI ingestion or manually document causes.
            </div>
          ) : (
            <div className="space-y-4">
              {rootCauses.map((cause: PotentialRootCause, index: number) => {
                const confidencePct = Math.round((cause.confidence || 0.8) * 100);
                const isConfirmed = cause.is_confirmed_by_qa;

                return (
                  <div
                    key={index}
                    className={`rounded-xl border p-5 transition-all shadow-xs ${
                      isConfirmed
                        ? 'border-emerald-300 bg-emerald-50/20'
                        : 'border-amber-200 bg-amber-50/20'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                      {/* Left: Cause details and supporting evidence */}
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center flex-wrap gap-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                            {cause.category || 'General'}
                          </span>

                          {/* Suggested - Unverified vs QA Verified pill */}
                          {isConfirmed ? (
                            <span className="inline-flex items-center space-x-1 text-[10px] font-bold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2.5 py-0.5 rounded-full shadow-2xs">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                              <span>QA Verified (Confirmed Root Cause)</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1 text-[10px] font-bold text-amber-900 bg-amber-100 border border-amber-300 px-2.5 py-0.5 rounded-full shadow-2xs animate-pulse">
                              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                              <span>Suggested – Unverified</span>
                            </span>
                          )}

                          {cause.is_ai_suggested && (
                            <span className="inline-flex items-center space-x-1 text-[10px] font-semibold text-cyan-800 bg-cyan-50 border border-cyan-200 px-2 py-0.5 rounded">
                              <Sparkles className="w-2.5 h-2.5 text-cyan-600" />
                              <span>AI Suggested</span>
                            </span>
                          )}
                        </div>

                        {/* Cause Title */}
                        <h5 className="text-xs font-bold text-slate-900 leading-snug">
                          {cause.cause}
                        </h5>

                        {/* Supporting Evidence Quote */}
                        {cause.supporting_evidence && (
                          <div className="text-xs text-slate-600 bg-white/90 border-l-2 border-indigo-400 pl-3 py-1.5 leading-relaxed rounded-r shadow-2xs">
                            <span className="font-semibold text-slate-700">Source Evidence: </span>
                            {cause.supporting_evidence}
                          </div>
                        )}
                      </div>

                      {/* Right: Confidence & QA Confirmation Toggle Button */}
                      <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-start gap-3 sm:min-w-[170px]">
                        <div className="text-right">
                          <div className="text-[10px] font-semibold text-slate-500">
                            Confidence Score:{' '}
                            <span className="font-bold text-slate-800">{confidencePct}%</span>
                          </div>
                          <div className="w-28 h-1.5 bg-slate-200 rounded-full overflow-hidden mt-1">
                            <div
                              className={`h-full ${
                                confidencePct >= 80
                                  ? 'bg-emerald-500'
                                  : confidencePct >= 60
                                  ? 'bg-amber-500'
                                  : 'bg-rose-500'
                              }`}
                              style={{ width: `${confidencePct}%` }}
                            ></div>
                          </div>
                        </div>

                        {/* Confirmation Toggle Button */}
                        <button
                          type="button"
                          onClick={() => dispatch(toggleRootCauseQA(index))}
                          className={`w-full sm:w-auto text-xs font-bold px-3 py-2 rounded-lg shadow-xs transition-all flex items-center justify-center space-x-1.5 ${
                            isConfirmed
                              ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                              : 'bg-white hover:bg-amber-100 text-amber-900 border border-amber-300'
                          }`}
                        >
                          {isConfirmed ? (
                            <>
                              <CheckCircle2 className="w-4 h-4 text-white" />
                              <span>Confirm Root Cause (QA Verified)</span>
                            </>
                          ) : (
                            <>
                              <ShieldCheck className="w-4 h-4 text-amber-700" />
                              <span>Confirm Root Cause (QA Verified)</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Evidence & Justification Input Box */}
                    <div className="mt-3 pt-3 border-t border-slate-200/80">
                      <label className="block text-[11px] font-bold text-slate-700 mb-1">
                        QA Verification Justification & Technical Evidence Record (ICH Q7):
                      </label>
                      <textarea
                        rows={2}
                        value={cause.qa_notes || ''}
                        onChange={(e) =>
                          dispatch(
                            updateRootCause({
                              index,
                              data: { qa_notes: e.target.value },
                            })
                          )
                        }
                        placeholder="Document verified instrument calibration tags, BMR cross-references, or lab assay results justifying QA confirmation..."
                        className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white leading-relaxed"
                      ></textarea>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
