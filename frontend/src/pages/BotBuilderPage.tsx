import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { createBot } from "../api/bots";
import type { Department } from "../api/types";
import Icon from "../components/Icon";

export default function BotBuilderPage() {
  const [name, setName] = useState("");
  const [department, setDepartment] = useState<Department>("maintenance");
  const [description, setDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [isShared, setIsShared] = useState(true);
  const [result, setResult] = useState<{ id: string; name: string }>();
  const [error, setError] = useState<string>();
  const [isSaving, setIsSaving] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError(undefined);
    setIsSaving(true);
    try {
      const bot = await createBot({
        name,
        department,
        description,
        system_prompt: systemPrompt,
        is_shared: isShared,
      });
      setResult({ id: bot.id, name: bot.name });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not create the assistant.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="page narrow-page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">BOT BUILDER</span>
          <h1>Create a focused <span>AI assistant.</span></h1>
          <p>Define its mission and the operating boundaries it must respect.</p>
        </div>
      </div>

      {result ? (
        <section className="success-card">
          <span><Icon name="check" /></span>
          <h2>{result.name} is ready.</h2>
          <p>The assistant is available in this demo session and can be opened immediately.</p>
          <div className="button-row">
            <Link className="primary-button" to={`/assistant?bot=${result.id}`}>Open assistant</Link>
            <button className="secondary-button" type="button" onClick={() => setResult(undefined)}>
              Create another
            </button>
          </div>
        </section>
      ) : (
        <form className="builder-form" onSubmit={submit}>
          <div className="form-section-heading">
            <span><Icon name="bot" /></span><div><h2>Assistant profile</h2><p>What should people expect from it?</p></div>
          </div>
          <div className="field-grid">
            <label>
              <span>Assistant name</span>
              <input value={name} onChange={(event) => setName(event.target.value)} minLength={3} maxLength={80} required placeholder="Warranty Assistant" />
            </label>
            <label>
              <span>Department</span>
              <select value={department} onChange={(event) => setDepartment(event.target.value as Department)}>
                <option value="maintenance">Maintenance</option>
                <option value="operations">Operations</option>
                <option value="sales">Sales</option>
                <option value="support">Support</option>
                <option value="engineering">Engineering</option>
              </select>
            </label>
          </div>
          <label>
            <span>Description</span>
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} minLength={10} maxLength={240} required rows={3} placeholder="Describe the team problem this assistant solves." />
            <small>{description.length}/240</small>
          </label>

          <div className="form-section-heading top-border">
            <span><Icon name="shield" /></span><div><h2>Instructions</h2><p>Set a clear role, sources, and safety limits.</p></div>
          </div>
          <label>
            <span>System prompt</span>
            <textarea value={systemPrompt} onChange={(event) => setSystemPrompt(event.target.value)} minLength={20} maxLength={4000} required rows={7} placeholder="You are an enterprise fleet warranty assistant. Use only approved policy documents…" />
          </label>
          <label className="toggle-row">
            <input type="checkbox" checked={isShared} onChange={(event) => setIsShared(event.target.checked)} />
            <span><strong>Publish to the internal marketplace</strong><small>Other departments will be able to discover this assistant.</small></span>
          </label>
          {error && <div className="inline-error">{error}</div>}
          <div className="form-actions">
            <Link className="secondary-button" to="/marketplace">Cancel</Link>
            <button className="primary-button" disabled={isSaving} type="submit">{isSaving ? "Creating…" : "Create assistant"}</button>
          </div>
        </form>
      )}
    </div>
  );
}
