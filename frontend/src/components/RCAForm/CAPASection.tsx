import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { addCAPA, updateCAPA, removeCAPA } from '../../store/slices/rcaSlice';
import {
  ShieldCheck,
  Plus,
  Trash2,
  Calendar,
  User,
  Sparkles,
  Edit2,
  Check,
} from 'lucide-react';
import { CAPARecommendation, CAPAActionType, CAPAStatus } from '../../types';

export const CAPASection: React.FC = () => {
  const dispatch = useAppDispatch();
  const { capa_recommendations } = useAppSelector((state) => state.rca);
  const [filterType, setFilterType] = useState<'All' | 'Corrective' | 'Preventive'>('All');
  const [showAddForm, setShowAddForm] = useState<boolean>(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  // New CAPA form state
  const [newTitle, setNewTitle] = useState('');
  const [newType, setNewType] = useState<CAPAActionType>('Corrective');
  const [newDescription, setNewDescription] = useState('');
  const [newRationale, setNewRationale] = useState('');
  const [newOwner, setNewOwner] = useState('Quality Assurance / Operations');
  const [newDueDate, setNewDueDate] = useState(
    new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0]
  );
  const [newStatus, setNewStatus] = useState<CAPAStatus>('Proposed');

  // Edit CAPA form state
  const [editTitle, setEditTitle] = useState('');
  const [editType, setEditType] = useState<CAPAActionType>('Corrective');
  const [editDescription, setEditDescription] = useState('');
  const [editRationale, setEditRationale] = useState('');
  const [editOwner, setEditOwner] = useState('');
  const [editDueDate, setEditDueDate] = useState('');
  const [editStatus, setEditStatus] = useState<CAPAStatus>('Proposed');

  const filteredCapas = capa_recommendations.filter((c) => {
    if (filterType === 'All') return true;
    return c.action_type === filterType;
  });

  const handleStartEdit = (index: number, capa: CAPARecommendation) => {
    setEditingIndex(index);
    setEditTitle(capa.title);
    setEditType(capa.action_type);
    setEditDescription(capa.description);
    setEditRationale(capa.rationale);
    setEditOwner(capa.owner);
    setEditDueDate(capa.target_due_date ? capa.target_due_date.split('T')[0] : '');
    setEditStatus(capa.status);
  };

  const handleSaveEdit = (index: number) => {
    if (!editTitle.trim()) return;
    dispatch(
      updateCAPA({
        index,
        data: {
          title: editTitle.trim(),
          action_type: editType,
          description: editDescription.trim(),
          rationale: editRationale.trim(),
          owner: editOwner.trim(),
          target_due_date: editDueDate || null,
          status: editStatus,
        },
      })
    );
    setEditingIndex(null);
  };

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    const capaItem: CAPARecommendation = {
      action_type: newType,
      title: newTitle.trim(),
      description: newDescription.trim() || newTitle.trim(),
      rationale: newRationale.trim() || 'Addresses identified root cause mechanism.',
      owner: newOwner.trim() || 'Engineering & Operations',
      target_due_date: newDueDate,
      status: newStatus,
      is_ai_suggested: false,
    };

    dispatch(addCAPA(capaItem));
    setNewTitle('');
    setNewDescription('');
    setNewRationale('');
    setShowAddForm(false);
  };

  const handleStatusChange = (index: number, status: CAPAStatus) => {
    dispatch(updateCAPA({ index, data: { status } }));
  };

  const handleTypeChange = (index: number, action_type: CAPAActionType) => {
    dispatch(updateCAPA({ index, data: { action_type } }));
  };

  const correctiveCount = capa_recommendations.filter((c) => c.action_type === 'Corrective').length;
  const preventiveCount = capa_recommendations.filter((c) => c.action_type === 'Preventive').length;

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-emerald-700" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            4. CAPA Action Plan (ICH Q10)
          </h3>
          <span className="text-[10px] font-bold text-slate-500 bg-slate-200/70 px-2 py-0.5 rounded">
            {correctiveCount} Corrective • {preventiveCount} Preventive
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Filter Pills */}
          <div className="flex bg-slate-200/70 p-0.5 rounded-lg text-xs font-semibold">
            {(['All', 'Corrective', 'Preventive'] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setFilterType(t)}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  filterType === t
                    ? 'bg-white text-slate-900 shadow-xs font-bold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center space-x-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold py-1.5 px-3 rounded-lg shadow-xs transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Action</span>
          </button>
        </div>
      </div>

      <div className="p-6 space-y-5">
        <p className="text-xs text-slate-600 leading-relaxed">
          ICH Q10 Quality System mandates clear differentiation between immediate{' '}
          <strong className="text-amber-700">Corrective Actions (CA)</strong> to remediate the isolated deviation and systemic{' '}
          <strong className="text-emerald-700">Preventive Actions (PA)</strong> to preclude recurrence across manufacturing lines. Click any action to edit titles, owners, target due dates, or switch action types.
        </p>

        {/* Add CAPA Form */}
        {showAddForm && (
          <form
            onSubmit={handleAddSubmit}
            className="rounded-xl border border-emerald-300 bg-emerald-50/40 p-5 space-y-4 shadow-xs"
          >
            <div className="flex items-center justify-between pb-2 border-b border-emerald-200">
              <h4 className="text-xs font-bold text-emerald-950 uppercase tracking-wide">
                Define New CAPA Commitment
              </h4>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="text-xs text-slate-500 hover:text-slate-800"
              >
                Cancel
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">Action Type</label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value as CAPAActionType)}
                  className="w-full text-xs font-semibold p-2 border border-slate-300 rounded-lg bg-white"
                >
                  <option value="Corrective">Corrective (Fix isolated issue)</option>
                  <option value="Preventive">Preventive (Preclude recurrence)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">Status</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value as CAPAStatus)}
                  className="w-full text-xs font-semibold p-2 border border-slate-300 rounded-lg bg-white"
                >
                  <option value="Proposed">Proposed</option>
                  <option value="Approved">Approved</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">Target Owner</label>
                <input
                  type="text"
                  value={newOwner}
                  onChange={(e) => setNewOwner(e.target.value)}
                  placeholder="e.g. Mechanical Maintenance Lead"
                  className="w-full text-xs p-2 border border-slate-300 rounded-lg bg-white"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">Target Due Date</label>
                <input
                  type="date"
                  value={newDueDate}
                  onChange={(e) => setNewDueDate(e.target.value)}
                  className="w-full text-xs p-2 border border-slate-300 rounded-lg bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">CAPA Action Title</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Replace saturated desiccant bed AD-04 and recalibrate dew point probe"
                className="w-full text-xs font-semibold p-2 border border-slate-300 rounded-lg bg-white"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Detailed Implementation Protocol
                </label>
                <textarea
                  rows={2}
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Specific maintenance or QA procedural actions..."
                  className="w-full text-xs p-2 border border-slate-300 rounded-lg bg-white"
                ></textarea>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Technical Rationale (Root Cause Link)
                </label>
                <textarea
                  rows={2}
                  value={newRationale}
                  onChange={(e) => setNewRationale(e.target.value)}
                  placeholder="Explains why this action directly resolves the failure mechanism..."
                  className="w-full text-xs p-2 border border-slate-300 rounded-lg bg-white"
                ></textarea>
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-200 rounded"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-xs"
              >
                Save Action Item
              </button>
            </div>
          </form>
        )}

        {/* List of CAPA Cards */}
        {filteredCapas.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-400">
            <ShieldCheck className="w-10 h-10 mx-auto text-slate-300 mb-2" />
            <p className="text-xs font-semibold text-slate-600">No CAPA recommendations recorded.</p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Run AI analysis or click "Add Action" to establish corrective and preventive commitments.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredCapas.map((capa) => {
              const originalIndex = capa_recommendations.findIndex((c) => c === capa);
              const isEditing = editingIndex === originalIndex;
              const isCorrective = capa.action_type === 'Corrective';

              if (isEditing) {
                return (
                  <div
                    key={originalIndex}
                    className="rounded-xl border-2 border-indigo-400 bg-white p-5 space-y-4 shadow-sm"
                  >
                    <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                      <div className="flex items-center space-x-2">
                        <Edit2 className="w-4 h-4 text-indigo-600" />
                        <h4 className="text-xs font-bold text-slate-900 uppercase">
                          Editing CAPA #{originalIndex + 1}
                        </h4>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          type="button"
                          onClick={() => setEditingIndex(null)}
                          className="px-2.5 py-1 text-xs text-slate-600 hover:bg-slate-100 rounded"
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          onClick={() => handleSaveEdit(originalIndex)}
                          className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded flex items-center space-x-1"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>Save Changes</span>
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                      <div>
                        <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">
                          Action Type
                        </label>
                        <select
                          value={editType}
                          onChange={(e) => setEditType(e.target.value as CAPAActionType)}
                          className="w-full text-xs font-semibold p-2 border border-slate-300 rounded bg-white"
                        >
                          <option value="Corrective">Corrective</option>
                          <option value="Preventive">Preventive</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">
                          Status
                        </label>
                        <select
                          value={editStatus}
                          onChange={(e) => setEditStatus(e.target.value as CAPAStatus)}
                          className="w-full text-xs font-semibold p-2 border border-slate-300 rounded bg-white"
                        >
                          <option value="Proposed">Proposed</option>
                          <option value="Approved">Approved</option>
                          <option value="In Progress">In Progress</option>
                          <option value="Completed">Completed</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">
                          Assignee / Owner
                        </label>
                        <input
                          type="text"
                          value={editOwner}
                          onChange={(e) => setEditOwner(e.target.value)}
                          placeholder="e.g. Maintenance Lead"
                          className="w-full text-xs p-2 border border-slate-300 rounded bg-white"
                        />
                      </div>

                      <div>
                        <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">
                          Target Due Date
                        </label>
                        <input
                          type="date"
                          value={editDueDate}
                          onChange={(e) => setEditDueDate(e.target.value)}
                          className="w-full text-xs p-2 border border-slate-300 rounded bg-white"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">
                        CAPA Action Title
                      </label>
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        className="w-full text-xs font-semibold p-2 border border-slate-300 rounded bg-white"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">
                          Implementation Protocol
                        </label>
                        <textarea
                          rows={2}
                          value={editDescription}
                          onChange={(e) => setEditDescription(e.target.value)}
                          className="w-full text-xs p-2 border border-slate-300 rounded bg-white leading-relaxed"
                        ></textarea>
                      </div>

                      <div>
                        <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">
                          Technical Rationale
                        </label>
                        <textarea
                          rows={2}
                          value={editRationale}
                          onChange={(e) => setEditRationale(e.target.value)}
                          className="w-full text-xs p-2 border border-slate-300 rounded bg-white leading-relaxed"
                        ></textarea>
                      </div>
                    </div>
                  </div>
                );
              }

              return (
                <div
                  key={originalIndex}
                  className={`rounded-xl border p-4 transition-all hover:shadow-xs ${
                    isCorrective
                      ? 'border-amber-200 bg-amber-50/20'
                      : 'border-emerald-200 bg-emerald-50/20'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center flex-wrap gap-2">
                        {/* Switch Action Type dropdown */}
                        <select
                          value={capa.action_type}
                          onChange={(e) =>
                            handleTypeChange(originalIndex, e.target.value as CAPAActionType)
                          }
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full border cursor-pointer focus:outline-none ${
                            isCorrective
                              ? 'bg-amber-100 text-amber-900 border-amber-300'
                              : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                          }`}
                        >
                          <option value="Corrective">Corrective Action</option>
                          <option value="Preventive">Preventive Action</option>
                        </select>

                        {capa.is_ai_suggested && (
                          <span className="inline-flex items-center space-x-1 text-[10px] font-semibold text-cyan-800 bg-cyan-50 border border-cyan-200 px-1.5 py-0.5 rounded">
                            <Sparkles className="w-2.5 h-2.5 text-cyan-600" />
                            <span>AI Suggested</span>
                          </span>
                        )}

                        {/* Status dropdown */}
                        <div className="flex items-center space-x-1">
                          <label className="text-[10px] text-slate-500 font-semibold">Status:</label>
                          <select
                            value={capa.status}
                            onChange={(e) =>
                              handleStatusChange(originalIndex, e.target.value as CAPAStatus)
                            }
                            className={`text-[10px] font-bold px-2 py-0.5 rounded border focus:outline-none cursor-pointer ${
                              capa.status === 'Completed'
                                ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                                : capa.status === 'In Progress'
                                ? 'bg-blue-100 text-blue-800 border-blue-300'
                                : 'bg-slate-100 text-slate-800 border-slate-300'
                            }`}
                          >
                            <option value="Proposed">Proposed</option>
                            <option value="Approved">Approved</option>
                            <option value="In Progress">In Progress</option>
                            <option value="Completed">Completed</option>
                          </select>
                        </div>
                      </div>

                      {/* Title */}
                      <h4 className="text-xs font-bold text-slate-900 leading-snug">{capa.title}</h4>

                      {/* Description */}
                      <p className="text-xs text-slate-600 leading-relaxed">{capa.description}</p>

                      {/* Rationale */}
                      {capa.rationale && (
                        <div className="text-xs text-slate-600 bg-white/80 border-l-2 border-slate-300 pl-3 py-1 rounded-r leading-relaxed shadow-2xs">
                          <span className="font-semibold text-slate-700">Root Cause Link: </span>
                          {capa.rationale}
                        </div>
                      )}

                      {/* Meta Tags: Owner & Due Date */}
                      <div className="flex items-center flex-wrap gap-4 pt-1 text-[11px] text-slate-500">
                        <div className="flex items-center space-x-1.5">
                          <User className="w-3.5 h-3.5 text-slate-400" />
                          <span>Owner: </span>
                          <span className="font-semibold text-slate-700">{capa.owner || 'Unassigned'}</span>
                        </div>

                        {capa.target_due_date && (
                          <div className="flex items-center space-x-1.5">
                            <Calendar className="w-3.5 h-3.5 text-slate-400" />
                            <span>Target Completion: </span>
                            <span className="font-mono font-semibold text-slate-700">
                              {capa.target_due_date.split('T')[0]}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action buttons: Edit & Delete */}
                    <div className="flex sm:flex-col items-center sm:items-end justify-between gap-1">
                      <button
                        type="button"
                        onClick={() => handleStartEdit(originalIndex, capa)}
                        title="Edit all fields of this CAPA action"
                        className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors flex items-center space-x-1 text-xs"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                        <span className="text-[11px] font-semibold hidden sm:inline">Edit</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => dispatch(removeCAPA(originalIndex))}
                        title="Delete CAPA recommendation"
                        className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded transition-colors flex items-center space-x-1 text-xs"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        <span className="text-[11px] font-semibold hidden sm:inline">Delete</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
