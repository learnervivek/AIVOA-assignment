import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  InvestigationSummary,
  InvestigationDetail,
  SeverityLevel,
  InvestigationStatus,
  SourceType,
  WhyItem,
  Fishbone6M,
  PotentialRootCause,
  MissingEvidenceItem,
  CAPARecommendation,
  AIWorkflowResult,
} from '../../types';
import {
  getInvestigations,
  getInvestigation,
  createInvestigation,
  updateInvestigation,
  deleteInvestigation as apiDeleteInvestigation,
} from '../../services/api';

export interface FormFields {
  id: string | null;
  deviation_number: string;
  title: string;
  api_product_name: string;
  batch_lot_number: string;
  equipment_id: string;
  manufacturing_stage: string;
  incident_date: string;
  severity: SeverityLevel;
  description: string;
  immediate_containment: string;
  raw_input_text: string;
  source_type: SourceType;
  status: InvestigationStatus;
}

export interface RCAAnalysisState {
  id?: string;
  methodology: '5_whys' | 'fishbone';
  five_whys_data: WhyItem[];
  fishbone_6m_data: Fishbone6M;
  potential_root_causes: PotentialRootCause[];
  missing_evidence: MissingEvidenceItem[];
}

export type FieldProvenance = 'ai_extracted' | 'user_edited' | 'unmodified';

export interface RCAState {
  form: FormFields;
  rca_analysis: RCAAnalysisState;
  capa_recommendations: CAPARecommendation[];
  aiPopulatedFields: Record<string, boolean>;
  fieldProvenance: Record<string, FieldProvenance>;
  savedInvestigations: InvestigationSummary[];
  selectedInvestigationId: string | null;
  loading: boolean;
  saveStatus: 'idle' | 'saving' | 'saved' | 'error';
  errorMessage: string | null;
  toastMessage: string | null;
}

const initialForm: FormFields = {
  id: null,
  deviation_number: '',
  title: '',
  api_product_name: '',
  batch_lot_number: '',
  equipment_id: '',
  manufacturing_stage: '',
  incident_date: new Date().toISOString(),
  severity: 'Major',
  description: '',
  immediate_containment: '',
  raw_input_text: '',
  source_type: 'text',
  status: 'Draft',
};

const initialRCAAnalysis: RCAAnalysisState = {
  methodology: 'fishbone',
  five_whys_data: [],
  fishbone_6m_data: {
    man: [],
    machine: [],
    material: [],
    method: [],
    measurement: [],
    environment: [],
  },
  potential_root_causes: [],
  missing_evidence: [],
};

const initialState: RCAState = {
  form: initialForm,
  rca_analysis: initialRCAAnalysis,
  capa_recommendations: [],
  aiPopulatedFields: {},
  fieldProvenance: {},
  savedInvestigations: [],
  selectedInvestigationId: null,
  loading: false,
  saveStatus: 'idle',
  errorMessage: null,
  toastMessage: null,
};

// Async Thunks
export const fetchInvestigationsThunk = createAsyncThunk(
  'rca/fetchInvestigations',
  async (_, { rejectWithValue }) => {
    try {
      const data = await getInvestigations();
      return data;
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to fetch investigations');
    }
  }
);

export const loadInvestigationThunk = createAsyncThunk(
  'rca/loadInvestigation',
  async (id: string, { rejectWithValue }) => {
    try {
      const detail: InvestigationDetail = await getInvestigation(id);
      return detail;
    } catch (err: any) {
      return rejectWithValue(err.message || `Failed to load investigation ${id}`);
    }
  }
);

export const saveInvestigationThunk = createAsyncThunk(
  'rca/saveInvestigation',
  async (_, { getState, rejectWithValue }) => {
    const state = getState() as { rca: RCAState };
    const { form, rca_analysis, capa_recommendations } = state.rca;

    try {
      const payload: any = {
        deviation_number: form.deviation_number || `DEV-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`,
        title: form.title || 'Untitled Deviation',
        api_product_name: form.api_product_name || 'Active Pharmaceutical Ingredient',
        batch_lot_number: form.batch_lot_number || 'LOT-PENDING',
        equipment_id: form.equipment_id || 'EQ-GENERAL',
        manufacturing_stage: form.manufacturing_stage || 'Manufacturing / Isolation',
        incident_date: form.incident_date || new Date().toISOString(),
        severity: form.severity,
        description: form.description || 'No description provided.',
        immediate_containment: form.immediate_containment || null,
        raw_input_text: form.raw_input_text || null,
        source_type: form.source_type,
        status: form.status,
        rca_analysis: {
          methodology: rca_analysis.methodology,
          five_whys_data: rca_analysis.five_whys_data,
          fishbone_6m_data: rca_analysis.fishbone_6m_data,
          potential_root_causes: rca_analysis.potential_root_causes,
          missing_evidence: rca_analysis.missing_evidence,
        },
        capa_recommendations: capa_recommendations.map((c) => ({
          action_type: c.action_type,
          title: c.title,
          description: c.description,
          rationale: c.rationale,
          owner: c.owner,
          target_due_date: c.target_due_date || null,
          status: c.status,
          is_ai_suggested: c.is_ai_suggested,
        })),
      };

      if (form.id) {
        const updated = await updateInvestigation(form.id, payload);
        return updated;
      } else {
        const created = await createInvestigation(payload);
        return created;
      }
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to save investigation');
    }
  }
);

export const deleteInvestigationThunk = createAsyncThunk(
  'rca/deleteInvestigation',
  async (id: string, { rejectWithValue }) => {
    try {
      await apiDeleteInvestigation(id);
      return id;
    } catch (err: any) {
      return rejectWithValue(err.message || 'Failed to delete investigation');
    }
  }
);

export const rcaSlice = createSlice({
  name: 'rca',
  initialState,
  reducers: {
    updateFormField: (
      state,
      action: PayloadAction<{ field: keyof FormFields; value: any }>
    ) => {
      (state.form as any)[action.payload.field] = action.payload.value;
      // When user edits a field, mark it as human-edited
      state.aiPopulatedFields[action.payload.field] = false;
      state.fieldProvenance[action.payload.field] = 'user_edited';
      state.saveStatus = 'idle';
    },

    setFormFromAI: (state, action: PayloadAction<AIWorkflowResult>) => {
      const data = action.payload;
      const dev = data.deviation_fields || {};
      const newAiPopulated: Record<string, boolean> = {};
      const newProvenance: Record<string, FieldProvenance> = {};

      if (dev.deviation_number) {
        state.form.deviation_number = dev.deviation_number;
        newAiPopulated.deviation_number = true;
        newProvenance.deviation_number = 'ai_extracted';
      }
      if (dev.title) {
        state.form.title = dev.title;
        newAiPopulated.title = true;
        newProvenance.title = 'ai_extracted';
      }
      if (dev.api_product_name) {
        state.form.api_product_name = dev.api_product_name;
        newAiPopulated.api_product_name = true;
        newProvenance.api_product_name = 'ai_extracted';
      }
      if (dev.batch_lot_number) {
        state.form.batch_lot_number = dev.batch_lot_number;
        newAiPopulated.batch_lot_number = true;
        newProvenance.batch_lot_number = 'ai_extracted';
      }
      if (dev.equipment_id) {
        state.form.equipment_id = dev.equipment_id;
        newAiPopulated.equipment_id = true;
        newProvenance.equipment_id = 'ai_extracted';
      }
      if (dev.manufacturing_stage) {
        state.form.manufacturing_stage = dev.manufacturing_stage;
        newAiPopulated.manufacturing_stage = true;
        newProvenance.manufacturing_stage = 'ai_extracted';
      }
      if (dev.incident_date) {
        state.form.incident_date = dev.incident_date;
        newAiPopulated.incident_date = true;
        newProvenance.incident_date = 'ai_extracted';
      }
      if (dev.severity) {
        state.form.severity = dev.severity;
        newAiPopulated.severity = true;
        newProvenance.severity = 'ai_extracted';
      }
      if (dev.description) {
        state.form.description = dev.description;
        newAiPopulated.description = true;
        newProvenance.description = 'ai_extracted';
      }
      if (dev.immediate_containment) {
        state.form.immediate_containment = dev.immediate_containment;
        newAiPopulated.immediate_containment = true;
        newProvenance.immediate_containment = 'ai_extracted';
      }
      if (data.raw_text) {
        state.form.raw_input_text = data.raw_text;
      }
      if (data.source_type) {
        state.form.source_type = data.source_type as SourceType;
      }

      state.aiPopulatedFields = {
        ...state.aiPopulatedFields,
        ...newAiPopulated,
      };
      state.fieldProvenance = {
        ...state.fieldProvenance,
        ...newProvenance,
      };

      // Set RCA analysis
      state.rca_analysis = {
        methodology: (data.preferred_methodology as any) || 'fishbone',
        five_whys_data: data.five_whys_data || [],
        fishbone_6m_data: data.fishbone_6m_data || initialRCAAnalysis.fishbone_6m_data,
        potential_root_causes: data.potential_root_causes || [],
        missing_evidence: data.missing_evidence || [],
      };

      // Set CAPA recommendations
      state.capa_recommendations = data.capa_recommendations || [];
      state.saveStatus = 'idle';
    },

    resetForm: (state) => {
      state.form = {
        ...initialForm,
        deviation_number: `DEV-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`,
        incident_date: new Date().toISOString(),
      };
      state.rca_analysis = initialRCAAnalysis;
      state.capa_recommendations = [];
      state.aiPopulatedFields = {};
      state.fieldProvenance = {};
      state.selectedInvestigationId = null;
      state.saveStatus = 'idle';
      state.errorMessage = null;
      state.toastMessage = null;
    },

    clearToast: (state) => {
      state.toastMessage = null;
    },

    setMethodology: (state, action: PayloadAction<'5_whys' | 'fishbone'>) => {
      state.rca_analysis.methodology = action.payload;
      state.saveStatus = 'idle';
    },

    confirmRootCause: (
      state,
      action: PayloadAction<{ index: number; qaNotes?: string }>
    ) => {
      const cause = state.rca_analysis.potential_root_causes[action.payload.index];
      if (cause) {
        cause.is_confirmed_by_qa = true;
        cause.qa_notes = action.payload.qaNotes || 'QA confirmed based on technical evidence review.';
        state.saveStatus = 'idle';
      }
    },

    toggleRootCauseQA: (state, action: PayloadAction<number>) => {
      const cause = state.rca_analysis.potential_root_causes[action.payload];
      if (cause) {
        cause.is_confirmed_by_qa = !cause.is_confirmed_by_qa;
        state.saveStatus = 'idle';
      }
    },

    dismissMissingEvidence: (state, action: PayloadAction<number>) => {
      if (action.payload >= 0 && action.payload < state.rca_analysis.missing_evidence.length) {
        state.rca_analysis.missing_evidence.splice(action.payload, 1);
        state.saveStatus = 'idle';
      }
    },

    addCAPA: (state, action: PayloadAction<CAPARecommendation>) => {
      state.capa_recommendations.push(action.payload);
      state.saveStatus = 'idle';
    },

    updateCAPA: (
      state,
      action: PayloadAction<{ index: number; data: Partial<CAPARecommendation> }>
    ) => {
      const item = state.capa_recommendations[action.payload.index];
      if (item) {
        state.capa_recommendations[action.payload.index] = {
          ...item,
          ...action.payload.data,
        };
      }
      state.saveStatus = 'idle';
    },

    removeCAPA: (state, action: PayloadAction<number>) => {
      if (action.payload >= 0 && action.payload < state.capa_recommendations.length) {
        state.capa_recommendations.splice(action.payload, 1);
        state.saveStatus = 'idle';
      }
    },

    updateWhyItem: (
      state,
      action: PayloadAction<{ index: number; why?: string; answer?: string }>
    ) => {
      const item = state.rca_analysis.five_whys_data[action.payload.index];
      if (item) {
        if (action.payload.why !== undefined) item.why = action.payload.why;
        if (action.payload.answer !== undefined) item.answer = action.payload.answer;
        state.saveStatus = 'idle';
      }
    },

    addWhyItem: (state) => {
      const currentLevel = state.rca_analysis.five_whys_data.length + 1;
      state.rca_analysis.five_whys_data.push({
        level: currentLevel,
        why: `Why did step ${currentLevel - 1} occur?`,
        answer: '',
      });
      state.saveStatus = 'idle';
    },

    removeWhyItem: (state, action: PayloadAction<number>) => {
      if (action.payload >= 0 && action.payload < state.rca_analysis.five_whys_data.length) {
        state.rca_analysis.five_whys_data.splice(action.payload, 1);
        // Re-index levels
        state.rca_analysis.five_whys_data.forEach((w, idx) => {
          w.level = idx + 1;
        });
        state.saveStatus = 'idle';
      }
    },

    updateRootCause: (
      state,
      action: PayloadAction<{ index: number; data: Partial<PotentialRootCause> }>
    ) => {
      const cause = state.rca_analysis.potential_root_causes[action.payload.index];
      if (cause) {
        state.rca_analysis.potential_root_causes[action.payload.index] = {
          ...cause,
          ...action.payload.data,
        };
        state.saveStatus = 'idle';
      }
    },

    addFishboneFactor: (
      state,
      action: PayloadAction<{ category: keyof Fishbone6M; factor: string }>
    ) => {
      const { category, factor } = action.payload;
      if (!factor.trim()) return;
      if (!state.rca_analysis.fishbone_6m_data[category]) {
        state.rca_analysis.fishbone_6m_data[category] = [];
      }
      state.rca_analysis.fishbone_6m_data[category].push(factor.trim());
      state.saveStatus = 'idle';
    },

    updateFishboneFactor: (
      state,
      action: PayloadAction<{ category: keyof Fishbone6M; index: number; factor: string }>
    ) => {
      const { category, index, factor } = action.payload;
      if (
        state.rca_analysis.fishbone_6m_data[category] &&
        index >= 0 &&
        index < state.rca_analysis.fishbone_6m_data[category].length
      ) {
        state.rca_analysis.fishbone_6m_data[category][index] = factor.trim();
        state.saveStatus = 'idle';
      }
    },

    removeFishboneFactor: (
      state,
      action: PayloadAction<{ category: keyof Fishbone6M; index: number }>
    ) => {
      const { category, index } = action.payload;
      if (
        state.rca_analysis.fishbone_6m_data[category] &&
        index >= 0 &&
        index < state.rca_analysis.fishbone_6m_data[category].length
      ) {
        state.rca_analysis.fishbone_6m_data[category].splice(index, 1);
        state.saveStatus = 'idle';
      }
    },
  },
  extraReducers: (builder) => {
    // 1. fetchInvestigationsThunk
    builder
      .addCase(fetchInvestigationsThunk.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchInvestigationsThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.savedInvestigations = action.payload;
        // If nothing selected and items exist, select the first one
        if (!state.selectedInvestigationId && action.payload.length > 0 && !state.form.id) {
          state.selectedInvestigationId = action.payload[0].id;
        }
      })
      .addCase(fetchInvestigationsThunk.rejected, (state, action) => {
        state.loading = false;
        state.errorMessage = action.payload as string;
      });

    // 2. loadInvestigationThunk
    builder
      .addCase(loadInvestigationThunk.pending, (state) => {
        state.loading = true;
        state.errorMessage = null;
      })
      .addCase(loadInvestigationThunk.fulfilled, (state, action) => {
        state.loading = false;
        const detail = action.payload;
        state.selectedInvestigationId = detail.id;

        state.form = {
          id: detail.id,
          deviation_number: detail.deviation_number,
          title: detail.title,
          api_product_name: detail.api_product_name,
          batch_lot_number: detail.batch_lot_number,
          equipment_id: detail.equipment_id,
          manufacturing_stage: detail.manufacturing_stage,
          incident_date: detail.incident_date,
          severity: detail.severity,
          description: detail.description,
          immediate_containment: detail.immediate_containment || '',
          raw_input_text: detail.raw_input_text || '',
          source_type: detail.source_type,
          status: detail.status,
        };

        const primaryRCA = detail.rca_analyses?.[0];
        if (primaryRCA) {
          state.rca_analysis = {
            id: primaryRCA.id,
            methodology: (primaryRCA.methodology as any) || 'fishbone',
            five_whys_data: primaryRCA.five_whys_data || [],
            fishbone_6m_data: primaryRCA.fishbone_6m_data || initialRCAAnalysis.fishbone_6m_data,
            potential_root_causes: primaryRCA.potential_root_causes || [],
            missing_evidence: primaryRCA.missing_evidence || [],
          };
        } else {
          state.rca_analysis = initialRCAAnalysis;
        }

        state.capa_recommendations = detail.capa_recommendations || [];
        state.aiPopulatedFields = {};
        state.saveStatus = 'idle';
      })
      .addCase(loadInvestigationThunk.rejected, (state, action) => {
        state.loading = false;
        state.errorMessage = action.payload as string;
      });

    // 3. saveInvestigationThunk
    builder
      .addCase(saveInvestigationThunk.pending, (state) => {
        state.saveStatus = 'saving';
        state.errorMessage = null;
      })
      .addCase(saveInvestigationThunk.fulfilled, (state, action) => {
        state.saveStatus = 'saved';
        const saved = action.payload;
        state.form.id = saved.id;
        state.selectedInvestigationId = saved.id;

        // Update in saved list or add
        const existingIdx = state.savedInvestigations.findIndex((i) => i.id === saved.id);
        const summary: InvestigationSummary = {
          ...saved,
          has_rca: saved.rca_analyses && saved.rca_analyses.length > 0,
          capa_count: saved.capa_recommendations?.length || 0,
        };
        if (existingIdx >= 0) {
          state.savedInvestigations[existingIdx] = summary;
        } else {
          state.savedInvestigations.unshift(summary);
        }
        state.toastMessage = `Investigation ${saved.deviation_number} successfully saved to PostgreSQL (21 CFR Part 11).`;
      })
      .addCase(saveInvestigationThunk.rejected, (state, action) => {
        state.saveStatus = 'error';
        state.errorMessage = action.payload as string;
      });

    // 4. deleteInvestigationThunk
    builder.addCase(deleteInvestigationThunk.fulfilled, (state, action) => {
      const deletedId = action.payload;
      state.savedInvestigations = state.savedInvestigations.filter((i) => i.id !== deletedId);
      if (state.selectedInvestigationId === deletedId) {
        const nextItem = state.savedInvestigations[0];
        state.selectedInvestigationId = nextItem ? nextItem.id : null;
        if (state.form.id === deletedId) {
          state.form = {
            ...initialForm,
            deviation_number: `DEV-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`,
            incident_date: new Date().toISOString(),
          };
          state.rca_analysis = initialRCAAnalysis;
          state.capa_recommendations = [];
          state.aiPopulatedFields = {};
          state.saveStatus = 'idle';
        }
      }
    });
  },
});

export const {
  updateFormField,
  setFormFromAI,
  resetForm,
  clearToast,
  setMethodology,
  confirmRootCause,
  toggleRootCauseQA,
  updateRootCause,
  dismissMissingEvidence,
  addCAPA,
  updateCAPA,
  removeCAPA,
  updateWhyItem,
  addWhyItem,
  removeWhyItem,
  addFishboneFactor,
  updateFishboneFactor,
  removeFishboneFactor,
} = rcaSlice.actions;

export default rcaSlice.reducer;
