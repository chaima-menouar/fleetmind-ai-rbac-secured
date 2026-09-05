export type Department = "maintenance" | "operations" | "sales" | "support" | "engineering";
export type UserRole = "admin" | "technician" | "viewer";

export interface CurrentUser {
  id: string;
  email: string;
  display_name: string;
  role: UserRole;
  department: string;
}

export interface AuthSession {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: CurrentUser;
}

export interface Bot {
  id: string;
  name: string;
  department: Department;
  description: string;
  system_prompt: string;
  knowledge_source_ids: string[];
  is_shared: boolean;
  created_at: string;
}

export interface ChatResponse {
  conversation_id: string;
  bot_id: string;
  content: string;
  sources: string[];
  created_at: string;
}

export interface Vehicle {
  id: string;
  model: string;
  driver: string;
  location: string;
  battery_percent: number;
  health_score: number;
  status: "active" | "attention" | "maintenance";
  next_service_days: number;
}

export interface FleetSummary {
  total_vehicles: number;
  active_vehicles: number;
  maintenance_due: number;
  average_health: number;
  vehicles: Vehicle[];
}

export interface FleetKpi {
  label: string;
  value: string;
  detail: string;
}

export interface FleetRisk {
  vehicle_id: string;
  model: string;
  location: string;
  risk_score: number;
  status: string;
  health_score: number;
  battery_percent: number;
  next_service_days: number;
}

export interface FleetIntelligence {
  generated_from: "deterministic_fleet_analytics";
  kpis: FleetKpi[];
  risk_ranking: FleetRisk[];
  critical_vehicle_ids: string[];
}

export interface AgentTask {
  task_id: string;
  status: "completed" | "failed";
  summary: string;
  output: {
    ticket: { ticket_id: string; status: string } | null;
    telemetry: Record<string, string | number>;
    steps_completed: number;
  };
  created_at: string;
}

export interface UsageStats {
  total_messages: number;
  total_agent_runs: number;
  active_conversations: number;
  published_bots: number;
  messages_by_bot: Record<string, number>;
}

export interface ModelCard {
  model_version: string;
  artifact_sha256: string;
  trained_at: string;
  algorithm: string;
  dataset: {
    name: string;
    source: string;
    doi: string;
    archive_sha256: string;
    license_catalog: string;
    train_rows: number;
    test_rows: number;
    features: number;
    train_positive_rows: number;
    test_positive_rows: number;
  };
  training: {
    random_state: number;
    fit_rows: number;
    calibration_rows: number;
    threshold_rows: number;
    decision_threshold: number;
    validation_cost: number;
    false_positive_cost: number;
    false_negative_cost: number;
  };
  metrics: {
    precision: number;
    recall: number;
    f1: number;
    balanced_accuracy: number;
    roc_auc: number;
    average_precision: number;
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
    official_cost: number;
    all_negative_baseline_cost: number;
    cost_reduction_percent: number;
  };
  limitations: string[];
}

export interface PredictionSample {
  sample_id: string;
}

export interface APSPrediction {
  sample_id: string;
  aps_failure_score: number;
  decision_threshold: number;
  predicted_label: "aps_failure" | "other_failure";
  actual_label: "aps_failure" | "other_failure";
  matches_actual: boolean;
  risk_level: "low" | "watch" | "high";
  model_version: string;
}
