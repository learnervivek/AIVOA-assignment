import {
  HealthResponse,
  ExtractionResult,
  InvestigationSummary,
  InvestigationDetail,
} from '../types';

export const checkSystemHealth = async (): Promise<HealthResponse> => {
  const response = await fetch('/health');
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
};

export const extractFile = async (file: File): Promise<ExtractionResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/investigations/extract-file', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `File extraction failed (${response.status})`);
  }
  return response.json();
};

export const extractRawText = async (
  content: string,
  sourceType: string = 'text',
  filename?: string
): Promise<ExtractionResult> => {
  const response = await fetch('/api/investigations/extract-text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content,
      source_type: sourceType,
      filename,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Text extraction failed (${response.status})`);
  }
  return response.json();
};

export const getInvestigations = async (): Promise<InvestigationSummary[]> => {
  const response = await fetch('/api/investigations');
  if (!response.ok) {
    throw new Error(`Failed to fetch investigations: ${response.statusText}`);
  }
  return response.json();
};

export const getInvestigation = async (id: string): Promise<InvestigationDetail> => {
  const response = await fetch(`/api/investigations/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch investigation ${id}: ${response.statusText}`);
  }
  return response.json();
};

export const createInvestigation = async (payload: any): Promise<InvestigationDetail> => {
  const response = await fetch('/api/investigations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create investigation (${response.status})`);
  }
  return response.json();
};

export const updateInvestigation = async (id: string, payload: any): Promise<InvestigationDetail> => {
  const response = await fetch(`/api/investigations/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update investigation (${response.status})`);
  }
  return response.json();
};

export const deleteInvestigation = async (id: string): Promise<{ success: boolean; message: string }> => {
  const response = await fetch(`/api/investigations/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to delete investigation (${response.status})`);
  }
  return response.json();
};

export const runAIAnalyze = async (
  rawText: string,
  sourceType: string = 'text',
  preferredMethodology: string = 'fishbone'
) => {
  const response = await fetch('/api/ai/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      raw_text: rawText,
      source_type: sourceType,
      preferred_methodology: preferredMethodology,
    }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `AI analysis failed (${response.status})`);
  }
  return response.json();
};

export const runAIRefine = async (currentState: any, instruction: string) => {
  const response = await fetch('/api/ai/refine', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      current_state: currentState,
      instruction,
    }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `AI refinement failed (${response.status})`);
  }
  return response.json();
};
