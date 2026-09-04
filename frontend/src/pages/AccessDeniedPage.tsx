import { Link } from "react-router-dom";
import Icon from "../components/Icon";

export default function AccessDeniedPage() {
  return (
    <div className="page narrow-page">
      <section className="access-denied-card">
        <span><Icon name="shield" /></span>
        <small>ROLE-PROTECTED AREA</small>
        <h1>Access is not available for your role.</h1>
        <p>Your account is active, but this function requires additional FleetMind permissions.</p>
        <Link className="primary-button" to="/">Return to your dashboard</Link>
      </section>
    </div>
  );
}
