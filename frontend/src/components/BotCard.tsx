import { Link } from "react-router-dom";
import type { Bot } from "../api/types";
import Icon, { type IconName } from "./Icon";

const departmentLabels: Record<string, string> = {
  maintenance: "Maintenance",
  operations: "Operations",
  sales: "Sales",
  support: "Support",
  engineering: "Engineering",
};

const departmentIcons: Record<string, IconName> = {
  maintenance: "wrench",
  operations: "route",
  sales: "briefcase",
  support: "headset",
  engineering: "code",
};

interface BotCardProps {
  bot: Bot;
}

export default function BotCard({ bot }: BotCardProps) {
  return (
    <article className="bot-card">
      <div className={`bot-symbol department-${bot.department}`} aria-hidden="true">
        <Icon name={departmentIcons[bot.department] ?? "bot"} />
      </div>
      <div className="bot-card-copy">
        <div className="bot-card-heading">
          <span className="eyebrow">{departmentLabels[bot.department] ?? bot.department}</span>
          {bot.is_shared && <span className="shared-badge">Shared</span>}
        </div>
        <h3>{bot.name}</h3>
        <p>{bot.description}</p>
        <div className="bot-card-footer">
          <span>{bot.knowledge_source_ids.length} knowledge sources</span>
          <Link className="text-link" to={`/assistant?bot=${bot.id}`}>Open assistant <span>→</span></Link>
        </div>
      </div>
    </article>
  );
}
