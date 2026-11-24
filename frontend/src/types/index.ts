export type SeverityLevel = 'Critical' | 'Major' | 'Minor';
export type InvestigationStatus = 'Draft' | 'Under Review' | 'QA Approved';
export type SourceType = 'pdf' | 'email' | 'text';

export interface Investigation {
  id: string;
  deviation_number: string;
  title: string;
  api_product_name: string;
  batch_lot_number: string;
  equipment_id: string;
  manufacturing_stage: string;
  incident_date: string;
  severity: SeverityLevel;
  description: string;
  immediate_containment?: string | null;
  raw_input_text?: string | null;
  source_type: SourceType;
  status: InvestigationStatus;
  created_at: string;
  updated_at: string;
}

export interface InvestigationSummary extends Investigation {
  has_rca: boolean;
  capa_count: number;
}

export interface WhyItem {
  level: number;
  why: string;
  answer: string;
}

export interface Fishbone6M {
  man: string[];
  machine: string[];
  material: string[];
  method: string[];
  measurement: string[];
  environment: string[];
}

export interface PotentialRootCause {
  cause: string;
  category: string;
  supporting_evidence: string;
  confidence: number;
  is_ai_suggested: boolean;
  is_confirmed_by_qa: boolean;
  qa_notes?: string | null;
}

export interface MissingEvidenceItem {
  gap: string;
  why_it_matters: string;
}

export interface RCAAnalysis {
  id?: string;
  investigation_id?: string;
  methodology: '5_whys' | 'fishbone' | 'hybrid';
  five_whys_data?: WhyItem[];
  fishbone_6m_data: Fishbone6M;
  potential_root_causes: PotentialRootCause[];
  missing_evidence: MissingEvidenceItem[];
  created_at?: string;
  updated_at?: string;
}

export type CAPAActionType = 'Corrective' | 'Preventive';
export type CAPAStatus = 'Proposed' | 'Approved' | 'In Progress' | 'Completed';

export interface CAPARecommendation {
  id?: string;
  investigation_id?: string;
  action_type: CAPAActionType;
  title: string;
  description: string;
  rationale: string;
  owner: string;
  target_due_date?: string | null;
  status: CAPAStatus;
  is_ai_suggested: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface InvestigationDetail extends Investigation {
  rca_analyses: RCAAnalysis[];
  capa_recommendations: CAPARecommendation[];
}

export interface ExtractionResult {
  filename: string;
  file_type: string;
  file_size_bytes: number;
  page_count: number;
  extracted_text: string;
  metadata: Record<string, any>;
  parsed_headers?: Record<string, string> | null;
  detected_entities: {
    deviation_numbers: string[];
    batch_lot_numbers: string[];
    equipment_ids: string[];
    severities: string[];
  };
}

export interface AIWorkflowResult {
  raw_text?: string;
  source_type?: string;
  preferred_methodology?: string;
  deviation_fields: {
    deviation_number?: string | null;
    title?: string;
    api_product_name?: string | null;
    batch_lot_number?: string | null;
    equipment_id?: string | null;
    manufacturing_stage?: string | null;
    incident_date?: string | null;
    severity?: SeverityLevel;
    description?: string;
    immediate_containment?: string | null;
  };
  missing_evidence: MissingEvidenceItem[];
  five_whys_data: WhyItem[];
  fishbone_6m_data: Fishbone6M;
  potential_root_causes: PotentialRootCause[];
  capa_recommendations: CAPARecommendation[];
  execution_logs?: string[];
  error?: string | null;
}

export type AIProcessingStage = 'idle' | 'extracting' | 'auditing' | 'rca' | 'capa' | 'completed' | 'error';

export interface AIChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
  database: {
    status: string;
    database: string;
    version?: string;
  };
}
