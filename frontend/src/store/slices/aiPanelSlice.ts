import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  AIWorkflowResult,
  AIProcessingStage,
  AIChatMessage,
} from '../../types';
import { extractFile, runAIAnalyze, runAIRefine } from '../../services/api';
import { setFormFromAI } from './rcaSlice';

export interface AIPanelState {
  inputTab: 'pdf' | 'email' | 'text';
  uploadedFileName: string | null;
  uploadedFileSize: number | null;
  pastedEmail: string;
  pastedText: string;
  preferredMethodology: 'fishbone' | '5_whys';
  processingStage: AIProcessingStage;
  stageProgress: number; // 0 to 100
  analysisResult: AIWorkflowResult | null;
  refinementHistory: AIChatMessage[];
  refinePrompt: string;
  isAnalyzing: boolean;
  isRefining: boolean;
  error: string | null;
}

const sampleEmailPreset = `From: production-shift-b@pharma-api.com
To: qa-compliance@pharma-api.com, engineering-lead@pharma-api.com
Date: 2026-11-23 14:15:00
Subject: URGENT: Deviation DEV-2026-0812 on Line 4 (Atorvastatin Calcium)

Dear QA & Operations Team,

During the vacuum drying stage of Atorvastatin Calcium Trihydrate batch ATC-2026-0881 in Tray Dryer VTD-01, temperature probe TT-201 spiked to 92°C for 45 minutes against the validated limit of NMT 80.0°C. 
Preliminary inspection suggests a heating steam regulator valve diaphragm rupture. 

Batch ATC-2026-0881 was immediately quarantined under QA Yellow Tag #Q-881. Line 4 drying has been placed on hold pending instrumentation inspection.`;

const sampleTextPreset = `During milling operations on Jet Mill MILL-PIN-02 for Metformin HCl lot MET-2026-0410, inline particle size analyzer reported D90 at 58.2 um (specification: NMT 45.0 um). 
Operator noted inlet nitrogen gas pressure had dropped to 4.8 bar instead of normal 6.8 bar. Saturated desiccant bed AD-04 suspected due to +15C dew point transmitter drift. 
Quarantined 250 kg milled bulk in quarantine bay 2.`;

const initialState: AIPanelState = {
  inputTab: 'pdf',
  uploadedFileName: null,
  uploadedFileSize: null,
  pastedEmail: sampleEmailPreset,
  pastedText: sampleTextPreset,
  preferredMethodology: 'fishbone',
  processingStage: 'idle',
  stageProgress: 0,
  analysisResult: null,
  refinementHistory: [],
  refinePrompt: '',
  isAnalyzing: false,
  isRefining: false,
  error: null,
};

// Async Thunks
export const analyzeDocumentThunk = createAsyncThunk(
  'aiPanel/analyzeDocument',
  async (
    payload: { file?: File; textOverride?: string },
    { getState, dispatch, rejectWithValue }
  ) => {
    const state = getState() as { aiPanel: AIPanelState };
    const { inputTab, pastedEmail, pastedText, preferredMethodology } = state.aiPanel;

    try {
      let rawText = '';
      let sourceType = 'text';

      dispatch(aiPanelSlice.actions.setProcessingStage('extracting'));
      dispatch(aiPanelSlice.actions.setStageProgress(25));

      if (inputTab === 'pdf') {
        if (!payload.file) {
          throw new Error('Please select a PDF file to analyze.');
        }
        // Extract text from PDF first
        const extraction = await extractFile(payload.file);
        rawText = extraction.extracted_text;
        sourceType = 'pdf';
      } else if (inputTab === 'email') {
        rawText = payload.textOverride || pastedEmail;
        sourceType = 'email';
      } else {
        rawText = payload.textOverride || pastedText;
        sourceType = 'text';
      }

      if (!rawText || !rawText.trim()) {
        throw new Error('Input text is empty. Please provide deviation details.');
      }

      dispatch(aiPanelSlice.actions.setProcessingStage('auditing'));
      dispatch(aiPanelSlice.actions.setStageProgress(50));

      // Call LangGraph AI analyze
      dispatch(aiPanelSlice.actions.setProcessingStage('rca'));
      dispatch(aiPanelSlice.actions.setStageProgress(75));

      const result: AIWorkflowResult = await runAIAnalyze(
        rawText,
        sourceType,
        preferredMethodology
      );

      dispatch(aiPanelSlice.actions.setProcessingStage('capa'));
      dispatch(aiPanelSlice.actions.setStageProgress(90));

      // Auto-apply to active RCA form
      dispatch(setFormFromAI(result));

      dispatch(aiPanelSlice.actions.setProcessingStage('completed'));
      dispatch(aiPanelSlice.actions.setStageProgress(100));

      // Add assistant welcome chat entry
      dispatch(
        aiPanelSlice.actions.addChatMessage({
          role: 'assistant',
          text: `Auto-populated RCA form for deviation ${
            result.deviation_fields?.deviation_number || 'record'
          } with ${result.potential_root_causes?.length || 0} root causes, 5-Whys, 6M Ishikawa, and ${
            result.capa_recommendations?.length || 0
          } CAPA items.`,
        })
      );

      return result;
    } catch (err: any) {
      dispatch(aiPanelSlice.actions.setProcessingStage('error'));
      return rejectWithValue(err.message || 'AI RCA analysis failed.');
    }
  }
);

export const refineRCAThunk = createAsyncThunk(
  'aiPanel/refineRCA',
  async (instruction: string, { getState, dispatch, rejectWithValue }) => {
    const rootState = getState() as { aiPanel: AIPanelState; rca: any };
    const { rca } = rootState;

    if (!instruction.trim()) {
      return rejectWithValue('Refinement instruction cannot be empty.');
    }

    try {
      dispatch(
        aiPanelSlice.actions.addChatMessage({
          role: 'user',
          text: instruction,
        })
      );

      const currentState = {
        deviation_fields: rca.form,
        five_whys_data: rca.rca_analysis.five_whys_data,
        fishbone_6m_data: rca.rca_analysis.fishbone_6m_data,
        potential_root_causes: rca.rca_analysis.potential_root_causes,
        capa_recommendations: rca.capa_recommendations,
        missing_evidence: rca.rca_analysis.missing_evidence,
      };

      const result: AIWorkflowResult = await runAIRefine(currentState, instruction);

      // Auto-apply refined outputs to the form
      dispatch(setFormFromAI(result));

      dispatch(
        aiPanelSlice.actions.addChatMessage({
          role: 'assistant',
          text: `Updated RCA and CAPA plan based on: "${instruction}"`,
        })
      );

      return result;
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to refine RCA with AI.');
    }
  }
);

export const aiPanelSlice = createSlice({
  name: 'aiPanel',
  initialState,
  reducers: {
    setInputTab: (state, action: PayloadAction<'pdf' | 'email' | 'text'>) => {
      state.inputTab = action.payload;
      state.error = null;
    },
    setUploadedFileInfo: (
      state,
      action: PayloadAction<{ name: string; size: number } | null>
    ) => {
      if (action.payload) {
        state.uploadedFileName = action.payload.name;
        state.uploadedFileSize = action.payload.size;
      } else {
        state.uploadedFileName = null;
        state.uploadedFileSize = null;
      }
    },
    setPastedEmail: (state, action: PayloadAction<string>) => {
      state.pastedEmail = action.payload;
    },
    setPastedText: (state, action: PayloadAction<string>) => {
      state.pastedText = action.payload;
    },
    setPreferredMethodology: (
      state,
      action: PayloadAction<'fishbone' | '5_whys'>
    ) => {
      state.preferredMethodology = action.payload;
    },
    setProcessingStage: (state, action: PayloadAction<AIProcessingStage>) => {
      state.processingStage = action.payload;
    },
    setStageProgress: (state, action: PayloadAction<number>) => {
      state.stageProgress = action.payload;
    },
    setRefinePrompt: (state, action: PayloadAction<string>) => {
      state.refinePrompt = action.payload;
    },
    addChatMessage: (
      state,
      action: PayloadAction<{ role: 'user' | 'assistant'; text: string }>
    ) => {
      state.refinementHistory.push({
        id: `msg-${Date.now()}-${Math.random()}`,
        role: action.payload.role,
        text: action.payload.text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      });
    },
    clearError: (state) => {
      state.error = null;
    },
    resetAIPanel: (state) => {
      state.processingStage = 'idle';
      state.stageProgress = 0;
      state.analysisResult = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // analyzeDocumentThunk
    builder
      .addCase(analyzeDocumentThunk.pending, (state) => {
        state.isAnalyzing = true;
        state.error = null;
      })
      .addCase(analyzeDocumentThunk.fulfilled, (state, action) => {
        state.isAnalyzing = false;
        state.analysisResult = action.payload;
      })
      .addCase(analyzeDocumentThunk.rejected, (state, action) => {
        state.isAnalyzing = false;
        state.error = action.payload as string;
      });

    // refineRCAThunk
    builder
      .addCase(refineRCAThunk.pending, (state) => {
        state.isRefining = true;
      })
      .addCase(refineRCAThunk.fulfilled, (state) => {
        state.isRefining = false;
        state.refinePrompt = '';
      })
      .addCase(refineRCAThunk.rejected, (state, action) => {
        state.isRefining = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setInputTab,
  setUploadedFileInfo,
  setPastedEmail,
  setPastedText,
  setPreferredMethodology,
  setProcessingStage,
  setStageProgress,
  setRefinePrompt,
  addChatMessage,
  clearError,
  resetAIPanel,
} = aiPanelSlice.actions;

export default aiPanelSlice.reducer;
