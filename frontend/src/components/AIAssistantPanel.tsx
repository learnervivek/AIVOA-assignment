import React, { useRef, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import {
  setInputTab,
  setUploadedFileInfo,
  setPastedEmail,
  setPastedText,
  setPreferredMethodology,
  setRefinePrompt,
  analyzeDocumentThunk,
  refineRCAThunk,
  clearError,
} from '../store/slices/aiPanelSlice';
import {
  Sparkles,
  UploadCloud,
  Mail,
  FileText,
  CheckCircle2,
  Clock,
  AlertCircle,
  Send,
  RefreshCw,
  Cpu,
  Layers,
  HelpCircle,
  Bot,
  User,
  FileCheck,
  BookmarkCheck,
} from 'lucide-react';

const SCENARIO_1_PDF_TEXT = `AIVOA PHARMACEUTICAL CHEMICALS CORP.
Active Pharmaceutical Ingredient (API) Manufacturing Facility
Quality Assurance & Regulatory Compliance Directorate
FORM: QMS-DEV-FORM-04 | Revision: 06 | ICH Q7 §12 & 21 CFR Part 211
OUT-OF-SPECIFICATION (OOS) DEVIATION INVESTIGATION REPORT

Deviation Number: DEV-2026-0914
Initial Severity: CRITICAL
Target API Product: Atorvastatin Calcium Trihydrate API
Batch / Lot Number: BAT-ATC-2026-0914
Manufacturing Stage: Reaction & Controlled Crystallization
Equipment ID Tag: REACT-CR-01 (3000L Glass-Lined)
Incident Date / Time: 2026-11-20 03:45:00 UTC
Investigation Status: Under Review

1. Description of Deviation Event & Analytical OOS Result:
During commercial manufacturing of Atorvastatin Calcium Trihydrate batch BAT-ATC-2026-0914 in Suite 3, the crystallization step in 3000L glass-lined reactor REACT-CR-01 suffered an uncontrolled thermal excursion. According to the Batch Manufacturing Record (BMR Page 42 of 68), the batch recipe mandates controlled linear cooling from 65.0°C down to 20.0°C ± 2.0°C over 6 hours under continuous 45 RPM dual-impeller agitation. At 03:45 UTC, cooling jacket control valve TCV-104 failed open due to pneumatic positioner signal loss, causing rapid chilling followed by operator bypass manipulation that overheated the jacket slurry to 38.5°C for 52 minutes.
Following wet milling and vacuum tray drying, QC Analytical Laboratory received final release sample QC-2026-914-A. High Performance Liquid Chromatography (HPLC) assay analysis on column C-18 (5 um, 250 x 4.6 mm) yielded an Assay of 94.2% w/w (anhydrous basis), which is Out-Of-Specification against the ICH Q7 validated specification limit of 98.0% - 102.0% w/w. The OOS was confirmed upon repeat duplicate injection by a second analyst.

2. Immediate Containment & Quarantine Actions:
1. Batch BAT-ATC-2026-0914 (Total 420.5 kg dry weight packaged in double polyethylene bags in fiber drums) was immediately placed under QA Yellow Quarantine Tag #Q-914 in Secure Quarantine Bay 3.
2. Reactor REACT-CR-01 was locked out and tagged out (LOTO #LOTO-CR01-11) pending engineering inspection of pneumatic valve TCV-104.
3. Downstream dispensing and packaging operations for Line 3 were halted.

3. Preliminary Technical Hypotheses:
• Machine/Instrumentation: Proportional pneumatic positioner on TCV-104 suffered diaphragm tear or 4-20mA DCS control loop signal drop.
• Method/Process: Thermal spike to 38.5°C induced polymorphic transformation and lactonization/solvolysis degradation during crystallization.
• Measurement: Potential HPLC system baseline integration error or standard preparation weight discrepancy.

4. Technical Evidence Audit Status (ICH Q7 §12 & §14):
NOTE FOR QA INVESTIGATOR: The following mandatory physical and analytical records are currently MISSING from the initial deviation intake package:
• Missing Item 1: HPLC Raw Integration Files, Chromatograms, and System Suitability sequence run for sample QC-2026-914-A (required to rule out chromatographic baseline drift or peak tailing).
• Missing Item 2: Calibration Certificate and Maintenance History for Reactor Temperature Transmitter TT-104 (last calibration overdue by 14 days per instrument tag).
• Missing Item 3: Mother Liquor Mass Balance & Crystallization Yield Analysis (necessary to verify if missing active ingredient partition dissolved into filtrate vs decomposed).`;

const SCENARIO_2_EMAIL_TEXT = `From: qc-analytical-lead@pharma-api.com
To: qa-compliance@pharma-api.com, chemical-operations@pharma-api.com, engineering-support@pharma-api.com
Date: 2026-11-22 09:30:00
Subject: CRITICAL DEVIATION: DEV-2026-1102 - Related Substance Impurity D Spike in Losartan Potassium Lot LOS-2026-1102

Dear QA Compliance & Operations Teams,

During final release testing of Losartan Potassium API lot LOS-2026-1102 produced on Line 3, QC chromatography reported an unexpected Out-of-Specification spike for Related Substance Impurity D (Dimer Adduct).

1. DEVIATION METADATA:
- Deviation Number: DEV-2026-1102
- Severity: Critical
- API Product Name: Losartan Potassium USP
- Batch / Lot Number: LOT-LOS-2026-1102
- Equipment ID Tag: FBD-02 (Fluid Bed Dryer Line 3)
- Manufacturing Stage: Final Drying & Solvent Evaporation
- Incident Date: 2026-11-22 08:15:00

2. EVENT DESCRIPTION:
HPLC purity testing performed under QC Protocol #SOP-QC-441 revealed Impurity D at 0.38% w/w. The validated release specification is NMT 0.15% w/w.
Batch processing records indicate this batch was dried in Fluid Bed Dryer FBD-02. Notably, during the final recrystallization wash step prior to drying, operations switched to a new solvent lot of Isopropanol (Supplier: ChemSupply Inc., Lot #CS-IPA-991), replacing our primary supplier lot.

3. IMMEDIATE CONTAINMENT:
Lot LOT-LOS-2026-1102 (310 kg bulk API) has been placed under QA Yellow Quarantine Tag #Q-1102 in Warehouse Bay 4. Solvent storage tank TK-IPA-03 has been locked out to prevent charging to subsequent batches.

4. MISSING TECHNICAL RECORDS NOTED BY QC:
- Critical Gap 1: Missing Confirmatory Testing & Certificate of Analysis (CoA) for raw material Isopropanol Lot #CS-IPA-991 (water content by Karl Fischer and peroxide value were not independently verified prior to vessel charging).
- Critical Gap 2: Missing FBD-02 inlet air HEPA filter differential pressure log and continuous moisture trap log (could not confirm drying chamber relative humidity during final 4 hours).
- Critical Gap 3: Missing Gas Chromatography (GC) head-space residual solvent chromatogram data for the affected batch.

Please initiate the RCA StateGraph workflow and notify Qualified Person (QP).`;

const SCENARIO_3_SHIFT_LOG_TEXT = `SHIFT B TO SHIFT C HANDOVER LOG & INCIDENT REPORT
================================================================================
Date/Time: 2026-11-23 18:00:00 UTC
Shift Supervisor: Mark Jenkins, Chemical Operations
Area: API Wet Cake Isolation Suite 4
================================================================================

1. DEVIATION IDENTIFICATION:
Deviation Number: DEV-2026-0520
Severity: Major
API Product Name: Clopidogrel Bisulfate Form I
Batch / Lot Number: BAT-CLP-2026-0520
Equipment Tag: CF-03 (Inverting Filter Centrifuge)
Manufacturing Stage: Wet Cake Isolation & Cake Washing
Incident Date: 2026-11-23 16:20:00

2. OPERATOR INCIDENT CHRONOLOGY:
- 16:05 UTC: Operator loaded crystallization slurry batch BAT-CLP-2026-0520 into Inverting Filter Centrifuge CF-03.
- 16:20 UTC: During the high-speed mother liquor spin (1200 RPM), operator observed the Nitrogen inerting blanket pressure transmitter PT-402 plunge from normal 50 mbar positive pressure down to 8 mbar (alarm threshold < 15 mbar).
- 16:22 UTC: Heavy vibration detected on drive shaft; minor hydrocarbon smoke smell noticed near the upper mechanical seal housing.
- 16:30 UTC: Operator performed emergency stop (E-Stop). Shift maintenance technician arrived and found the mechanical seal silicone-elastomer gasket degraded and leaking barrier fluid (mineral oil flush).
- 16:45 UTC: Technician replaced the mechanical seal gasket using a spare from workshop inventory (Part #GSK-SIL-88) without waiting for an Engineering Change Control (CC) form or QA engineering sign-off.
- 17:15 UTC: Centrifugation was restarted and 280 kg wet cake cake discharged into transfer bin TB-04.

3. IMMEDIATE CONTAINMENT / QUARANTINE:
- Wet cake transfer bin TB-04 tagged with QA Yellow Hold Tag #Q-0520.
- Centrifuge CF-03 placed on engineering hold.
- Sample pulled for visual particulate and lubricant contamination inspection.

4. INVESTIGATION GAPS / MISSING GMP RECORDS:
- Critical Gap 1: Missing Approved Engineering Change Control (CC) and Maintenance Work Order for the emergency gasket replacement on Centrifuge CF-03.
- Critical Gap 2: Missing Food/Pharma-Grade Lubricant Compatibility & Leachables Certificate for replacement seal gasket Part #GSK-SIL-88.
- Critical Gap 3: Missing Nitrogen header manifold pressure log and oxygen sensor analyzer (AO-102) calibration log during the pressure drop window.

Handed over to Shift C Lead (D. Vance) for QA Deviation initiation.`;

export const AIAssistantPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const {
    inputTab,
    uploadedFileName,
    uploadedFileSize,
    pastedEmail,
    pastedText,
    preferredMethodology,
    processingStage,
    stageProgress,
    refinementHistory,
    refinePrompt,
    isAnalyzing,
    isRefining,
    error,
  } = useAppSelector((state) => state.aiPanel);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      dispatch(setUploadedFileInfo({ name: file.name, size: file.size }));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      dispatch(setUploadedFileInfo({ name: file.name, size: file.size }));
    }
  };

  const handleSelectDemoScenario = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    if (val === 'scenario_pdf') {
      dispatch(setInputTab('text'));
      dispatch(setPastedText(SCENARIO_1_PDF_TEXT));
      dispatch(setPreferredMethodology('fishbone'));
    } else if (val === 'scenario_email') {
      dispatch(setInputTab('email'));
      dispatch(setPastedEmail(SCENARIO_2_EMAIL_TEXT));
      dispatch(setPreferredMethodology('fishbone'));
    } else if (val === 'scenario_log') {
      dispatch(setInputTab('text'));
      dispatch(setPastedText(SCENARIO_3_SHIFT_LOG_TEXT));
      dispatch(setPreferredMethodology('5_whys'));
    }
  };

  const handleRunAnalysis = () => {
    dispatch(analyzeDocumentThunk({ file: selectedFile || undefined }));
  };

  const handleSendRefinement = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!refinePrompt.trim() || isRefining) return;
    dispatch(refineRCAThunk(refinePrompt.trim()));
  };

  const handleChipClick = (chipText: string) => {
    dispatch(setRefinePrompt(chipText));
    dispatch(refineRCAThunk(chipText));
  };

  const stages = [
    { key: 'extracting', label: '1. Extract Deviation & Entities', desc: 'Zero hallucination parsing' },
    { key: 'auditing', label: '2. Senior QA Evidence Audit', desc: 'ICH Q7/Q9 gap detection' },
    { key: 'rca', label: '3. Formulate 5 Whys & 6M Fishbone', desc: 'Causal mechanisms' },
    { key: 'capa', label: '4. Recommend CAPA Plan', desc: 'Corrective & Preventive actions' },
  ];

  const getStageStatus = (stageKey: string) => {
    const order = ['idle', 'extracting', 'auditing', 'rca', 'capa', 'completed'];
    const currentIndex = order.indexOf(processingStage);
    const targetIndex = order.indexOf(stageKey);

    if (processingStage === 'error') return 'error';
    if (currentIndex > targetIndex || processingStage === 'completed') return 'completed';
    if (currentIndex === targetIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="w-full h-full bg-white border-l border-slate-200 flex flex-col justify-between overflow-hidden">
      {/* Panel Top Header */}
      <div className="px-5 py-4 border-b border-slate-200 bg-gradient-to-r from-slate-900 to-slate-800 text-white flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center text-cyan-400 shadow-sm">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold tracking-tight text-white flex items-center space-x-2">
                <span>AI RCA Co-Pilot</span>
                <span className="text-[10px] font-mono font-medium text-cyan-300 bg-cyan-900/60 px-1.5 py-0.2 rounded border border-cyan-600/50">
                  ICH Q7
                </span>
              </h2>
              <p className="text-[11px] text-slate-300 flex items-center space-x-1.5">
                <Cpu className="w-3 h-3 text-cyan-400" />
                <span>llama-3.3-70b-versatile via Groq</span>
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isAnalyzing || isRefining ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'
              }`}
            ></span>
            <span className="text-[11px] font-semibold text-slate-300">
              {isAnalyzing ? 'Analyzing' : isRefining ? 'Refining' : 'Ready'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Scrollable Content Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {/* Error Notification */}
        {error && (
          <div className="rounded-lg bg-rose-50 border border-rose-200 p-3 flex items-start justify-between gap-2 text-rose-800 text-xs">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => dispatch(clearError())}
              className="text-rose-500 hover:text-rose-800 text-[11px] font-bold"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Quick Demo Scenario Dropdown */}
        <div className="bg-gradient-to-r from-slate-50 to-cyan-50/30 border border-slate-200 rounded-xl p-3 space-y-1.5 shadow-2xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-800 flex items-center space-x-1.5">
              <BookmarkCheck className="w-3.5 h-3.5 text-cyan-700" />
              <span>Quick Demo Scenarios</span>
            </span>
            <span className="text-[9px] font-bold text-cyan-800 bg-cyan-100/70 border border-cyan-300 px-1.5 py-0.2 rounded-full">
              ICH Q7 Gaps Included
            </span>
          </div>
          <select
            onChange={handleSelectDemoScenario}
            defaultValue=""
            className="w-full text-xs font-semibold p-2 bg-white border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:ring-2 focus:ring-cyan-500 cursor-pointer"
          >
            <option value="" disabled>
              -- Select Realistic API Manufacturing Deviation --
            </option>
            <option value="scenario_pdf">
              Scenario 1 (PDF): Atorvastatin Temp Excursion & HPLC Assay OOS (DEV-2026-0914)
            </option>
            <option value="scenario_email">
              Scenario 2 (Email): Losartan Solvent Lot Switch & Impurity D Spike (DEV-2026-1102)
            </option>
            <option value="scenario_log">
              Scenario 3 (Shift Log): Clopidogrel Centrifuge Seal Failure & N2 Drop (DEV-2026-0520)
            </option>
          </select>
        </div>

        {/* Ingestion Source Tabs */}
        <div>
          <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wide mb-1.5">
            Ingestion Source
          </label>
          <div className="grid grid-cols-3 gap-1 bg-slate-100 p-1 rounded-lg text-xs font-semibold">
            <button
              type="button"
              onClick={() => dispatch(setInputTab('pdf'))}
              className={`py-1.5 rounded-md flex items-center justify-center space-x-1.5 transition-all ${
                inputTab === 'pdf'
                  ? 'bg-white text-slate-900 shadow-xs font-bold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Upload PDF</span>
            </button>

            <button
              type="button"
              onClick={() => dispatch(setInputTab('email'))}
              className={`py-1.5 rounded-md flex items-center justify-center space-x-1.5 transition-all ${
                inputTab === 'email'
                  ? 'bg-white text-slate-900 shadow-xs font-bold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Mail className="w-3.5 h-3.5" />
              <span>Paste Email</span>
            </button>

            <button
              type="button"
              onClick={() => dispatch(setInputTab('text'))}
              className={`py-1.5 rounded-md flex items-center justify-center space-x-1.5 transition-all ${
                inputTab === 'text'
                  ? 'bg-white text-slate-900 shadow-xs font-bold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Paste Text</span>
            </button>
          </div>
        </div>

        {/* Input Tab Contents */}
        {inputTab === 'pdf' && (
          <div className="space-y-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf"
              className="hidden"
            />
            <div
              role="button"
              tabIndex={0}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  fileInputRef.current?.click();
                }
              }}
              className="border-2 border-dashed border-slate-300 hover:border-cyan-500 rounded-xl p-5 text-center cursor-pointer transition-colors bg-slate-50/50 hover:bg-cyan-50/20 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <UploadCloud className="w-8 h-8 text-cyan-600 mx-auto mb-2" />
              <p className="text-xs font-bold text-slate-700">
                {uploadedFileName ? uploadedFileName : 'Select or drop incident PDF report'}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                {uploadedFileSize
                  ? `${(uploadedFileSize / 1024).toFixed(1)} KB`
                  : 'Choose sample_data/deviation_oos_assay.pdf or any batch investigation report'}
              </p>
            </div>

            {uploadedFileName && (
              <div className="rounded-lg bg-cyan-50 border border-cyan-200 p-2.5 flex items-center justify-between text-xs text-cyan-900">
                <div className="flex items-center space-x-2 truncate">
                  <FileCheck className="w-4 h-4 text-cyan-600 flex-shrink-0" />
                  <span className="font-semibold truncate">{uploadedFileName}</span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setSelectedFile(null);
                    if (fileInputRef.current) fileInputRef.current.value = '';
                    dispatch(setUploadedFileInfo(null));
                  }}
                  className="text-xs text-cyan-700 hover:text-cyan-950 font-bold ml-2"
                >
                  Clear
                </button>
              </div>
            )}
          </div>
        )}

        {inputTab === 'email' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-semibold">
                Shift Handover / Incident Email
              </span>
              <button
                type="button"
                onClick={() => dispatch(setPastedEmail(SCENARIO_2_EMAIL_TEXT))}
                className="text-[11px] text-cyan-700 hover:text-cyan-900 font-semibold flex items-center space-x-1"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Reset to Sample Email</span>
              </button>
            </div>
            <textarea
              rows={6}
              value={pastedEmail}
              onChange={(e) => dispatch(setPastedEmail(e.target.value))}
              placeholder="Paste raw email header and body here..."
              className="w-full text-xs font-mono p-3 border border-slate-300 rounded-lg focus:ring-1 focus:ring-cyan-500 focus:outline-none bg-slate-50/40 leading-relaxed"
            ></textarea>
          </div>
        )}

        {inputTab === 'text' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-semibold">
                Operator Shift Log / Equipment Notes
              </span>
              <button
                type="button"
                onClick={() => dispatch(setPastedText(SCENARIO_3_SHIFT_LOG_TEXT))}
                className="text-[11px] text-cyan-700 hover:text-cyan-900 font-semibold flex items-center space-x-1"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Reset to Sample Log</span>
              </button>
            </div>
            <textarea
              rows={6}
              value={pastedText}
              onChange={(e) => dispatch(setPastedText(e.target.value))}
              placeholder="Paste raw deviation notes or lab observations..."
              className="w-full text-xs font-mono p-3 border border-slate-300 rounded-lg focus:ring-1 focus:ring-cyan-500 focus:outline-none bg-slate-50/40 leading-relaxed"
            ></textarea>
          </div>
        )}

        {/* RCA Preferred Methodology Selector */}
        <div>
          <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wide mb-1.5">
            Initial Methodology Focus
          </label>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <label
              className={`flex items-center space-x-2 border rounded-lg p-2.5 cursor-pointer transition-all ${
                preferredMethodology === 'fishbone'
                  ? 'border-cyan-500 bg-cyan-50/40 text-cyan-950 font-bold'
                  : 'border-slate-200 bg-white text-slate-700'
              }`}
            >
              <input
                type="radio"
                name="methodology"
                checked={preferredMethodology === 'fishbone'}
                onChange={() => dispatch(setPreferredMethodology('fishbone'))}
                className="text-cyan-600 focus:ring-cyan-500 h-3.5 w-3.5"
              />
              <div className="flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-cyan-700" />
                <span>Ishikawa 6M</span>
              </div>
            </label>

            <label
              className={`flex items-center space-x-2 border rounded-lg p-2.5 cursor-pointer transition-all ${
                preferredMethodology === '5_whys'
                  ? 'border-cyan-500 bg-cyan-50/40 text-cyan-950 font-bold'
                  : 'border-slate-200 bg-white text-slate-700'
              }`}
            >
              <input
                type="radio"
                name="methodology"
                checked={preferredMethodology === '5_whys'}
                onChange={() => dispatch(setPreferredMethodology('5_whys'))}
                className="text-cyan-600 focus:ring-cyan-500 h-3.5 w-3.5"
              />
              <div className="flex items-center space-x-1.5">
                <HelpCircle className="w-3.5 h-3.5 text-indigo-700" />
                <span>5 Whys Chain</span>
              </div>
            </label>
          </div>
        </div>

        {/* Primary Action Button: Analyze & Auto-Populate Form */}
        <button
          type="button"
          onClick={handleRunAnalysis}
          disabled={isAnalyzing}
          className="w-full py-3.5 px-4 bg-gradient-to-r from-cyan-600 via-cyan-700 to-indigo-700 hover:from-cyan-700 hover:to-indigo-800 text-white font-bold text-xs rounded-xl shadow-md flex items-center justify-center space-x-2 transition-all transform active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isAnalyzing ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-white" />
              <span>Executing LangGraph RCA Workflow...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-cyan-200" />
              <span className="text-sm">Analyze & Auto-Populate Form</span>
            </>
          )}
        </button>

        {/* Step-by-Step Stepper Progress Bar */}
        {(isAnalyzing || processingStage !== 'idle') && (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-800">LangGraph Pipeline Progress</span>
              <span className="font-mono font-bold text-cyan-700">{stageProgress}%</span>
            </div>

            <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
              <div
                className="bg-cyan-600 h-full transition-all duration-300"
                style={{ width: `${stageProgress}%` }}
              ></div>
            </div>

            <div className="space-y-2 pt-1">
              {stages.map((stage) => {
                const status = getStageStatus(stage.key);
                return (
                  <div
                    key={stage.key}
                    className="flex items-center justify-between text-xs py-1 px-2 rounded"
                  >
                    <div className="flex items-center space-x-2">
                      {status === 'completed' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      ) : status === 'active' ? (
                        <Clock className="w-4 h-4 text-cyan-600 animate-spin flex-shrink-0" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-slate-300 flex-shrink-0"></div>
                      )}
                      <div>
                        <span
                          className={`font-semibold ${
                            status === 'active'
                              ? 'text-cyan-900 font-bold'
                              : status === 'completed'
                              ? 'text-slate-800'
                              : 'text-slate-400'
                          }`}
                        >
                          {stage.label}
                        </span>
                      </div>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">{stage.desc}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* AI Co-Pilot Conversation & Refinement History */}
        <div className="pt-2 border-t border-slate-200 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wide flex items-center space-x-1.5">
              <Bot className="w-3.5 h-3.5 text-cyan-600" />
              <span>Interactive Refinement</span>
            </span>
            <span className="text-[10px] text-slate-400 font-medium">Real-time Form Push</span>
          </div>

          {/* Quick Refinement Suggestion Chips */}
          <div className="flex flex-wrap gap-1.5">
            {[
              '+ Drill deeper into sensor drift',
              '+ Add operator retraining CAPA',
              '+ Detail cooling jacket Why #3',
              '+ Check solvent CoA Karl Fischer in 6M',
            ].map((chip) => (
              <button
                key={chip}
                type="button"
                onClick={() => handleChipClick(chip)}
                disabled={isRefining}
                className="text-[10px] font-medium text-slate-700 bg-slate-100 hover:bg-cyan-50 hover:text-cyan-800 border border-slate-200 hover:border-cyan-300 rounded-full px-2.5 py-1 transition-all disabled:opacity-50 cursor-pointer"
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Message List */}
          {refinementHistory.length > 0 && (
            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {refinementHistory.map((msg) => (
                <div
                  key={msg.id}
                  className={`rounded-lg p-2.5 text-xs leading-relaxed flex items-start space-x-2 ${
                    msg.role === 'user'
                      ? 'bg-indigo-50 border border-indigo-200 text-indigo-950 ml-4'
                      : 'bg-slate-50 border border-slate-200 text-slate-800 mr-4'
                  }`}
                >
                  {msg.role === 'user' ? (
                    <User className="w-3.5 h-3.5 text-indigo-600 mt-0.5 flex-shrink-0" />
                  ) : (
                    <Bot className="w-3.5 h-3.5 text-cyan-600 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <p>{msg.text}</p>
                    <span className="text-[9px] text-slate-400 block mt-1">{msg.timestamp}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Refinement Prompt Input Bar (Bottom Sticky) */}
      <div className="p-4 border-t border-slate-200 bg-slate-50 flex-shrink-0">
        <form onSubmit={handleSendRefinement} className="flex items-center space-x-2">
          <input
            type="text"
            value={refinePrompt}
            onChange={(e) => dispatch(setRefinePrompt(e.target.value))}
            placeholder="Ask AI to refine 5-Whys, probe sensors, or add CAPAs..."
            disabled={isRefining}
            className="flex-1 text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-1 focus:ring-cyan-500 focus:outline-none bg-white disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!refinePrompt.trim() || isRefining}
            className="p-2 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white rounded-lg transition-colors flex-shrink-0 cursor-pointer"
            title="Send instruction to AI Co-Pilot"
          >
            {isRefining ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
