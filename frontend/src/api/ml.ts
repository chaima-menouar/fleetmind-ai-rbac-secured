import { apiFetch } from "./client";
import type { APSPrediction, ModelCard, PredictionSample } from "./types";

export function getModelCard() {
  return apiFetch<ModelCard>("/api/ml/model-card");
}

export function getPredictionSamples() {
  return apiFetch<PredictionSample[]>("/api/ml/samples");
}

export function predictApsSample(sampleId: string) {
  return apiFetch<APSPrediction>("/api/ml/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sample_id: sampleId }),
  });
}

