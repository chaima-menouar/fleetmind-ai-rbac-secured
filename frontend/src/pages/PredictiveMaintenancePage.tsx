import { useEffect, useMemo, useState } from "react";
import { getModelCard, getPredictionSamples, predictApsSample } from "../api/ml";
import type { APSPrediction, ModelCard, PredictionSample } from "../api/types";
import StatCard from "../components/StatCard";
import Icon from "../components/Icon";
import { useAuth } from "../hooks/AuthContext";

const percent = (value: number) => `${(value * 100).toFixed(1)}%`;
const labelText = (value: string) => value === "aps_failure" ? "APS failure" : "Other failure";

function decisionExplanation(prediction: APSPrediction) {
  const margin = prediction.aps_failure_score - prediction.decision_threshold;
  const distance = Math.abs(margin);
  const confidence = distance >= 0.35 ? "Strong separation" : distance >= 0.15 ? "Moderate separation" : "Near decision threshold";
  const direction = margin >= 0 ? "above" : "below";
  const recommendation = prediction.predicted_label === "aps_failure"
    ? "Prioritize inspection of the APS-related maintenance pathway before returning the asset to service."
    : "No APS-specific intervention is indicated by this model output; continue normal diagnostics for other failure causes."
  return {
    confidence,
    marginText: `${percent(distance)} ${direction} threshold`,
    recommendation,
  };
}

export default function PredictiveMaintenancePage() {
  const { user } = useAuth();
  const canAnalyze = user?.role !== "viewer";
  const [card, setCard] = useState<ModelCard>();
  const [samples, setSamples] = useState<PredictionSample[]>([]);
  const [selected, setSelected] = useState("");
  const [prediction, setPrediction] = useState<APSPrediction>();
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    Promise.all([getModelCard(), getPredictionSamples()])
      .then(([modelCard, evaluationSamples]) => {
        setCard(modelCard);
        setSamples(evaluationSamples);
        setSelected(evaluationSamples[0]?.sample_id ?? "");
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load the model."))
      .finally(() => setLoading(false));
  }, []);

  const selectedPosition = useMemo(
    () => samples.findIndex((sample) => sample.sample_id === selected) + 1,
    [samples, selected],
  );
  const explanation = prediction ? decisionExplanation(prediction) : undefined;

  const runPrediction = async () => {
    if (!selected) return;
    setRunning(true);
    setError(undefined);
    try {
      setPrediction(await predictApsSample(selected));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Prediction failed.");
    } finally {
      setRunning(false);
    }
  };

  if (loading) return <div className="loading-card">Loading the trained APS model…</div>;

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">AI MAINTENANCE</span>
          <h1>Find risk early. <span>Keep vehicles moving.</span></h1>
          <p>FleetMind analyzes held-out sensor records and explains the model decision without mixing them with fictional fleet telemetry.</p>
        </div>
        <span className="verified-badge">✓ Held-out evaluation</span>
      </div>

      {error && <div className="inline-error">{error}</div>}

      {card && (
        <>
          <section className="panel-card prediction-lab featured-prediction">
            <div className="section-heading">
              <div><h2>Vehicle health check</h2><p>Analyze a real, held-out vehicle sensor record</p></div>
              <span>{samples.length} verified examples</span>
            </div>
            <div className="prediction-workspace">
              <div className="prediction-controls">
                <label htmlFor="sample-select">Vehicle sensor record</label>
                <select id="sample-select" value={selected} onChange={(event) => { setSelected(event.target.value); setPrediction(undefined); }}>
                  {samples.map((sample, index) => <option key={sample.sample_id} value={sample.sample_id}>Vehicle record {String(index + 1).padStart(2, "0")}</option>)}
                </select>
                <small>Record {selectedPosition} of {samples.length}. The confirmed outcome is revealed after analysis.</small>
                <button className="primary-button" type="button" onClick={() => void runPrediction()} disabled={!canAnalyze || !selected || running}>
                  {!canAnalyze ? "Viewer access · read only" : running ? "Analyzing sensors…" : "Analyze maintenance risk"}
                </button>
              </div>

              {prediction && explanation ? (
                <div className={`prediction-result risk-${prediction.risk_level}`}>
                  <div className="score-ring" style={{ "--score": `${Math.min(prediction.aps_failure_score * 360, 360)}deg` } as React.CSSProperties}>
                    <span><strong>{percent(prediction.aps_failure_score)}</strong><small>APS score</small></span>
                  </div>
                  <div className="prediction-copy">
                    <span className={`result-status ${prediction.matches_actual ? "correct" : "incorrect"}`}>
                      {prediction.matches_actual ? "Verified result" : "Review required"}
                    </span>
                    <h3>{prediction.predicted_label === "aps_failure" ? "APS service pathway flagged" : "APS pathway not flagged"}</h3>
                    <p>Confirmed outcome: <strong>{labelText(prediction.actual_label)}</strong></p>
                    <p><strong>{explanation.confidence}</strong> · {explanation.marginText}</p>
                    <p>{explanation.recommendation}</p>
                    <small>Decision threshold {percent(prediction.decision_threshold)} · {prediction.model_version}</small>
                  </div>
                </div>
              ) : (
                <div className="prediction-empty"><span><Icon name="pulse" /></span><p>Select a vehicle record and let FleetMind assess its maintenance risk.</p></div>
              )}
            </div>
          </section>

          <section className="data-boundary-banner">
            <div>
              <strong>Explainability boundary</strong>
              <span>The Scania features are anonymized, so FleetMind explains score, threshold distance, evaluation truth, and action scope without inventing physical sensor meanings.</span>
            </div>
          </section>

          <details className="model-evidence">
            <summary>View model performance and technical evidence</summary>
            <div className="stat-grid model-stat-grid">
              <StatCard label="Failure recall" value={percent(card.metrics.recall)} detail="349 of 375 APS failures detected" tone="green" />
              <StatCard label="Precision" value={percent(card.metrics.precision)} detail="Share of alerts that were APS failures" />
              <StatCard label="Average precision" value={percent(card.metrics.average_precision)} detail="Ranking quality under class imbalance" tone="violet" />
              <StatCard label="Cost reduction" value={`${card.metrics.cost_reduction_percent.toFixed(1)}%`} detail="Versus predicting no APS failures" tone="amber" />
            </div>

            <div className="model-grid">
              <section className="panel-card model-card">
                <div className="section-heading">
                  <div><h2>Model & dataset card</h2><p>Traceable training and evaluation facts</p></div>
                  <span>{card.model_version}</span>
                </div>
                <dl className="model-facts">
                  <div><dt>Dataset</dt><dd>{card.dataset.name}</dd></div>
                  <div><dt>Algorithm</dt><dd>{card.algorithm}</dd></div>
                  <div><dt>Official training split</dt><dd>{card.dataset.train_rows.toLocaleString()} rows · {card.dataset.train_positive_rows.toLocaleString()} APS failures</dd></div>
                  <div><dt>Untouched test split</dt><dd>{card.dataset.test_rows.toLocaleString()} rows · {card.dataset.test_positive_rows.toLocaleString()} APS failures</dd></div>
                  <div><dt>Input</dt><dd>{card.dataset.features} anonymized operational features</dd></div>
                  <div><dt>Decision threshold</dt><dd>{percent(card.training.decision_threshold)} · cost-sensitive</dd></div>
                </dl>
                <div className="source-row">
                  <a href={card.dataset.doi} target="_blank" rel="noreferrer">Open official dataset ↗</a>
                  <span>{card.dataset.license_catalog}</span>
                </div>
              </section>

              <section className="panel-card confusion-card">
                <div className="section-heading">
                  <div><h2>Confusion matrix</h2><p>All 16,000 official test rows</p></div>
                  <span>Threshold {percent(card.training.decision_threshold)}</span>
                </div>
                <div className="confusion-grid" aria-label="Confusion matrix">
                  <div className="matrix-axis corner">Actual ↓ · Predicted →</div>
                  <div className="matrix-axis">Other</div>
                  <div className="matrix-axis">APS</div>
                  <div className="matrix-axis">Other</div>
                  <div className="matrix-cell good"><strong>{card.metrics.true_negatives.toLocaleString()}</strong><span>True negatives</span></div>
                  <div className="matrix-cell warn"><strong>{card.metrics.false_positives.toLocaleString()}</strong><span>False alerts</span></div>
                  <div className="matrix-axis">APS</div>
                  <div className="matrix-cell danger"><strong>{card.metrics.false_negatives.toLocaleString()}</strong><span>Missed failures</span></div>
                  <div className="matrix-cell good"><strong>{card.metrics.true_positives.toLocaleString()}</strong><span>Detected failures</span></div>
                </div>
              </section>
            </div>
            <section className="model-notice">
              <strong>Model scope</strong>
              <p>{card.limitations.join(" ")}</p>
            </section>
          </details>
        </>
      )}
    </div>
  );
}
