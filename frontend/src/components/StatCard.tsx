interface StatCardProps {
  label: string;
  value: string | number;
  detail: string;
  tone?: "blue" | "green" | "amber" | "violet";
}

export default function StatCard({ label, value, detail, tone = "blue" }: StatCardProps) {
  const icons: Record<NonNullable<StatCardProps["tone"]>, IconName> = {
    blue: "chart",
    green: "pulse",
    amber: "fleet",
    violet: "sparkles",
  };

  return (
    <article className={`stat-card tone-${tone}`}>
      <div className="stat-card-head"><span className="stat-label">{label}</span><span className="stat-icon"><Icon name={icons[tone]} /></span></div>
      <strong className="stat-value">{value}</strong>
      <small>{detail}</small>
      <span className="stat-glow" />
    </article>
  );
}
import Icon, { type IconName } from "./Icon";
