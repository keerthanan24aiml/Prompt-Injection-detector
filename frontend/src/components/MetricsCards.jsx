
import { Activity, ShieldAlert, ShieldCheck } from "lucide-react";

export default function MetricsCards({ metrics }) {
  const cards = [
    { title: "Total Scanned", value: metrics.total, icon: Activity, color: "text-cyan-400" },
    { title: "Prompts Blocked", value: metrics.blocked, icon: ShieldAlert, color: "text-red-400" },
    { title: "Prompts Allowed", value: metrics.allowed, icon: ShieldCheck, color: "text-emerald-400" },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.title} className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-400">{card.title}</p>
              <Icon className={`h-6 w-6 ${card.color}`} />
            </div>
            <p className="mt-4 text-3xl font-bold text-white">{card.value}</p>
          </div>
        );
      })}
    </div>
  );
}
