import { Component, type ErrorInfo, type ReactNode } from "react";

interface State { error?: Error }

export default class AppErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = {};

  static getDerivedStateFromError(error: Error): State { return { error }; }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("FleetMind failed to render", error, info);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <main className="fatal-screen">
        <div>
          <span>FLEETMIND</span>
          <h1>We could not open your workspace.</h1>
          <p>{this.state.error.message || "An unexpected browser error occurred."}</p>
          <button type="button" onClick={() => { try { localStorage.clear(); sessionStorage.clear(); } catch { /* Ignore unavailable storage. */ } window.location.assign("/login"); }}>Reset local session</button>
        </div>
      </main>
    );
  }
}
