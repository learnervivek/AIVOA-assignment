import React from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { updateFormField } from '../../store/slices/rcaSlice';
import { SeverityLevel, InvestigationStatus } from '../../types';
import {
  Package,
  Wrench,
  Layers,
  Clock,
  Sparkles,
  Edit3,
  AlertTriangle,
  ShieldAlert,
  FileText,
  Calendar,
} from 'lucide-react';

export const DeviationOverviewSection: React.FC = () => {
  const dispatch = useAppDispatch();
  const { form, fieldProvenance } = useAppSelector((state) => state.rca);

  const handleFieldChange = (field: any, value: any) => {
    dispatch(updateFormField({ field, value }));
  };

  const isMissing = (value: string | null | undefined) => {
    return !value || !value.toString().trim();
  };

  const renderProvenancePill = (field: string, value: string | null | undefined, isRequired: boolean = true) => {
    const prov = fieldProvenance[field];
    const missing = isMissing(value);

    if (missing && isRequired) {
      return (
        <span className="inline-flex items-center space-x-1 text-[10px] font-bold text-amber-900 bg-amber-100 border border-amber-300 px-1.5 py-0.5 rounded-full ml-1.5 animate-pulse">
          <AlertTriangle className="w-2.5 h-2.5 text-amber-700" />
          <span>Missing from source</span>
        </span>
      );
    }

    if (prov === 'ai_extracted') {
      return (
        <span className="inline-flex items-center space-x-1 text-[10px] font-bold text-cyan-800 bg-cyan-50 border border-cyan-200 px-1.5 py-0.5 rounded-full ml-1.5">
          <Sparkles className="w-2.5 h-2.5 text-cyan-600" />
          <span>AI Extracted</span>
        </span>
      );
    }

    if (prov === 'user_edited') {
      return (
        <span className="inline-flex items-center space-x-1 text-[10px] font-bold text-slate-700 bg-slate-100 border border-slate-300 px-1.5 py-0.5 rounded-full ml-1.5">
          <Edit3 className="w-2.5 h-2.5 text-slate-600" />
          <span>Edited</span>
        </span>
      );
    }

    return null;
  };

  const getInputClasses = (value: string | null | undefined, baseExtra: string = '', isRequired: boolean = true) => {
    const missing = isMissing(value);
    if (missing && isRequired) {
      return `w-full text-xs p-2.5 border-2 border-amber-400 bg-amber-50/50 rounded-lg focus:ring-2 focus:ring-amber-500 focus:outline-none transition-all ${baseExtra}`;
    }
    return `w-full text-xs p-2.5 border border-slate-300 bg-white rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none transition-all ${baseExtra}`;
  };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
      {/* Section Header */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-cyan-700" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
            1. Deviation & Batch Overview
          </h3>
          <span className="text-[10px] font-bold text-slate-500 bg-slate-200/70 px-2 py-0.5 rounded">
            ICH Q7 API Context
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <label htmlFor="qa-status-select" className="text-xs font-semibold text-slate-600">
            QA Status:
          </label>
          <select
            id="qa-status-select"
            value={form.status}
            onChange={(e) => handleFieldChange('status', e.target.value as InvestigationStatus)}
            className="text-xs font-semibold bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-slate-800 focus:outline-none focus:ring-1 focus:ring-cyan-500"
          >
            <option value="Draft">Draft</option>
            <option value="Under Review">Under Review</option>
            <option value="QA Approved">QA Approved</option>
          </select>
        </div>
      </div>

      <div className="p-6 space-y-5">
        {/* Helper bar explaining Provenance & Missing Highlighting */}
        <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-600">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-700">Audit Provenance:</span>
            <span className="inline-flex items-center space-x-1 text-[10px] font-bold text-cyan-800 bg-cyan-100/60 border border-cyan-200 px-1.5 py-0.2 rounded-full">
              <Sparkles className="w-2.5 h-2.5 text-cyan-600" />
              <span>AI Extracted</span>
            </span>
            <span className="text-slate-400">→</span>
            <span className="inline-flex items-center space-x-1 text-[10px] font-bold text-slate-700 bg-slate-200 border border-slate-300 px-1.5 py-0.2 rounded-full">
              <Edit3 className="w-2.5 h-2.5 text-slate-600" />
              <span>Edited</span>
            </span>
          </div>
          <div className="flex items-center space-x-1.5 text-amber-800">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
            <span>Amber borders indicate mandatory GMP fields absent from source input.</span>
          </div>
        </div>

        {/* Row 1: Deviation ID, Severity, Title */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="deviation-number" className="flex items-center text-xs font-semibold text-slate-700 mb-1">
              <span>Deviation Number</span>
              {renderProvenancePill('deviation_number', form.deviation_number)}
            </label>
            <input
              id="deviation-number"
              type="text"
              value={form.deviation_number}
              onChange={(e) => handleFieldChange('deviation_number', e.target.value)}
              placeholder="e.g. DEV-2026-0812"
              className={getInputClasses(form.deviation_number, 'font-mono font-semibold')}
            />
          </div>

          <div>
            <label className="flex items-center text-xs font-semibold text-slate-700 mb-1">
              <span>Severity Rating</span>
              {renderProvenancePill('severity', form.severity)}
            </label>
            <div
              role="radiogroup"
              aria-label="Deviation Severity"
              className="flex rounded-lg border border-slate-300 overflow-hidden text-xs"
            >
              {(['Critical', 'Major', 'Minor'] as SeverityLevel[]).map((level) => (
                <button
                  key={level}
                  type="button"
                  role="radio"
                  aria-checked={form.severity === level}
                  onClick={() => handleFieldChange('severity', level)}
                  className={`flex-1 py-2 font-bold transition-all ${
                    form.severity === level
                      ? level === 'Critical'
                        ? 'bg-rose-600 text-white'
                        : level === 'Major'
                        ? 'bg-amber-600 text-white'
                        : 'bg-blue-600 text-white'
                      : 'bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label htmlFor="incident-date" className="flex items-center text-xs font-semibold text-slate-700 mb-1">
              <span>Incident Date/Time</span>
              {renderProvenancePill('incident_date', form.incident_date)}
            </label>
            <div className="relative">
              <Calendar className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-400" />
              <input
                id="incident-date"
                type="text"
                value={form.incident_date}
                onChange={(e) => handleFieldChange('incident_date', e.target.value)}
                placeholder="2026-11-23T14:30:00Z"
                className={getInputClasses(form.incident_date, 'pl-8 font-mono')}
              />
            </div>
          </div>
        </div>

        {/* Title */}
        <div>
          <label htmlFor="deviation-title" className="flex items-center text-xs font-semibold text-slate-700 mb-1">
            <span>Deviation Title</span>
            {renderProvenancePill('title', form.title)}
          </label>
          <input
            id="deviation-title"
            type="text"
            value={form.title}
            onChange={(e) => handleFieldChange('title', e.target.value)}
            placeholder="Short technical summary of the deviation"
            className={getInputClasses(form.title, 'font-semibold')}
          />
        </div>

        {/* Row 2: Product Name, Batch Lot, Equipment, Stage */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label htmlFor="api-product-name" className="flex items-center text-xs font-semibold text-slate-700 mb-1">
              <Package className="w-3.5 h-3.5 mr-1 text-cyan-600" />
              <span>Target API Product</span>
              {renderProvenancePill('api_product_name', form.api_product_name)}
            </label>
            <input
              id="api-product-name"
              type="text"
              value={form.api_product_name}
              onChange={(e) => handleFieldChange('api_product_name', e.target.value)}
              placeholder="e.g. Atorvastatin Calcium"
              className={getInputClasses(form.api_product_name)}
            />
          </div>

          <div>
            <label htmlFor="batch-lot-number" className="flex items-center text-xs font-semibold text-slate-700 mb-1">
              <Layers className="w-3.5 h-3.5 mr-1 text-cyan-600" />
              <span>Batch / Lot Number</span>
              {renderProvenancePill('batch_lot_number', form.batch_lot_number)}
            </label>
            <input
              id="batch-lot-number"
              type="text"
              value={form.batch_lot_number}
              onChange={(e) => handleFieldChange('batch_lot_number', e.target.value)}
              placeholder="e.g. BAT-2026-0881"
              className={getInputClasses(form.batch_lot_number, 'font-mono')}
            />
          </div>

          <div>
            <label htmlFor="equipment-id" className="flex items-center text-xs font-semibold text-slate-700 mb-1">
              <Wrench className="w-3.5 h-3.5 mr-1 text-cyan-600" />
              <span>Equipment ID Tag</span>
              {renderProvenancePill('equipment_id', form.equipment_id)}
            </label>
            <input
              id="equipment-id"
              type="text"
              value={form.equipment_id}
              onChange={(e) => handleFieldChange('equipment_id', e.target.value)}
              placeholder="e.g. MILL-PIN-02, VTD-01"
              className={getInputClasses(form.equipment_id, 'font-mono')}
            />
          </div>

          <div>
            <label htmlFor="manufacturing-stage" className="flex items-center text-xs font-semibold text-slate-700 mb-1">
              <Clock className="w-3.5 h-3.5 mr-1 text-cyan-600" />
              <span>Manufacturing Stage</span>
              {renderProvenancePill('manufacturing_stage', form.manufacturing_stage)}
            </label>
            <input
              id="manufacturing-stage"
              type="text"
              value={form.manufacturing_stage}
              onChange={(e) => handleFieldChange('manufacturing_stage', e.target.value)}
              placeholder="e.g. Crystallization, Drying"
              className={getInputClasses(form.manufacturing_stage)}
            />
          </div>
        </div>

        {/* Description & Containment */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="deviation-description" className="flex items-center text-xs font-semibold text-slate-700 mb-1">
              <span>Deviation Description (OOS / Parameter Event)</span>
              {renderProvenancePill('description', form.description)}
            </label>
            <textarea
              id="deviation-description"
              rows={4}
              value={form.description}
              onChange={(e) => handleFieldChange('description', e.target.value)}
              placeholder="Detailed description of what occurred, when, and specific limit exceeded..."
              className={getInputClasses(form.description, 'leading-relaxed')}
            ></textarea>
          </div>

          <div>
            <label htmlFor="immediate-containment" className="flex items-center text-xs font-semibold text-rose-700 mb-1">
              <ShieldAlert className="w-3.5 h-3.5 mr-1 text-rose-600" />
              <span>Immediate GMP Containment / Quarantine</span>
              {renderProvenancePill('immediate_containment', form.immediate_containment)}
            </label>
            <textarea
              id="immediate-containment"
              rows={4}
              value={form.immediate_containment}
              onChange={(e) => handleFieldChange('immediate_containment', e.target.value)}
              placeholder="e.g. Batch placed under QA Yellow tag #Q-881. Mill feed suspended. Retained samples pulled for re-assay..."
              className={`w-full text-xs p-2.5 rounded-lg focus:outline-none transition-all leading-relaxed ${
                isMissing(form.immediate_containment)
                  ? 'border-2 border-amber-400 bg-amber-50/50 focus:ring-2 focus:ring-amber-500'
                  : 'border border-rose-300 bg-rose-50/30 focus:ring-2 focus:ring-rose-500'
              }`}
            ></textarea>
          </div>
        </div>
      </div>
    </div>
  );
};
