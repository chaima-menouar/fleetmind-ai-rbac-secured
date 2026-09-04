export type IconName =
  | "sparkles"
  | "fleet"
  | "pulse"
  | "store"
  | "bot"
  | "chart"
  | "shield"
  | "send"
  | "wrench"
  | "route"
  | "briefcase"
  | "headset"
  | "code"
  | "check"
  | "database";

interface IconProps {
  name: IconName;
  className?: string;
}

export default function Icon({ name, className = "" }: IconProps) {
  const paths: Record<IconName, React.ReactNode> = {
    sparkles: <><path d="m12 3 1.1 3.4a4 4 0 0 0 2.5 2.5L19 10l-3.4 1.1a4 4 0 0 0-2.5 2.5L12 17l-1.1-3.4a4 4 0 0 0-2.5-2.5L5 10l3.4-1.1a4 4 0 0 0 2.5-2.5L12 3Z"/><path d="m19 16 .5 1.5a2 2 0 0 0 1 1L22 19l-1.5.5a2 2 0 0 0-1 1L19 22l-.5-1.5a2 2 0 0 0-1-1L16 19l1.5-.5a2 2 0 0 0 1-1L19 16Z"/></>,
    fleet: <><path d="M3 7h12l3 4h2a1 1 0 0 1 1 1v5h-2"/><path d="M5 17H3V5a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v12h-3"/><circle cx="8" cy="17" r="2"/><circle cx="16" cy="17" r="2"/><path d="M10 17h4"/></>,
    pulse: <><path d="M3 12h4l2-6 4 12 2-6h6"/><path d="M5 4a9 9 0 1 1-2 12" opacity=".45"/></>,
    store: <><path d="M4 10v10h16V10"/><path d="M3 4h18l-2 6a3 3 0 0 1-4 1 3 3 0 0 1-6 0 3 3 0 0 1-4-1L3 4Z"/><path d="M9 20v-6h6v6"/></>,
    bot: <><rect x="4" y="7" width="16" height="13" rx="3"/><path d="M12 3v4M8 12h.01M16 12h.01M8 16h8"/></>,
    chart: <><path d="M4 19V9M10 19V5M16 19v-7M22 19V3"/><path d="M2 19h22"/></>,
    shield: <><path d="M12 3 20 6v6c0 5-3.4 8-8 10-4.6-2-8-5-8-10V6l8-3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></>,
    send: <><path d="m4 4 17 8-17 8 3-8-3-8Z"/><path d="M7 12h14"/></>,
    wrench: <><path d="M14.7 6.3a4 4 0 0 0-5-5L12 3.6 9.6 6 7.3 3.7a4 4 0 0 0 5 5L4 17l3 3 7.7-8.3a4 4 0 0 0 0-5.4Z"/></>,
    route: <><circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h3a3 3 0 0 0 3-3V9a3 3 0 0 1 3-3"/></>,
    briefcase: <><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v2h4v-2"/></>,
    headset: <><path d="M4 14v-2a8 8 0 0 1 16 0v2"/><path d="M4 14h3v6H5a2 2 0 0 1-2-2v-2a2 2 0 0 1 1-2ZM20 14h-3v6h2a2 2 0 0 0 2-2v-2a2 2 0 0 0-1-2Z"/></>,
    code: <><path d="m8 9-4 3 4 3M16 9l4 3-4 3M14 5l-4 14"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    database: <><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></>,
  };

  return (
    <svg className={`icon ${className}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {paths[name]}
    </svg>
  );
}

