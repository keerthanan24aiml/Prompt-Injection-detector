
import { ShieldCheck, ShieldAlert } from "lucide-react";

export default function SecurityInspector({ result }) {
  if (!result) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-lg font-bold text-white">Security Inspector</h2>
        <p className="mt-12 text-center text-slate-500">
          Waiting for prompt analysis...
        </p>
      </section>
    );
  }

  const blocked = result.decision === "BLOCK";
  const risk = Math.max(0, Math.min(100, Number(result.risk_score) || 0));

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <h2 className="text-lg font-bold text-white">Security Inspector</h2>

      <div className="mt-6 flex items-center gap-3">
        {blocked
          ? <ShieldAlert className="h-10 w-10 text-red-400" />
          : <ShieldCheck className="h-10 w-10 text-emerald-400" />}
        <div>
          <p className={`text-2xl font-bold ${blocked ? "text-red-400" : "text-emerald-400"}`}>
            {result.decision}
          </p>
          <p className="text-xs text-slate-400">Security decision</p>
        </div>
      </div>

      <div className="mt-8">
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Risk score</span>
          <span className="text-white">{risk.toFixed(1)}/100</span>
        </div>
        <div className="mt-3 h-3 rounded-full bg-slate-800">
          <div
            className={`h-3 rounded-full ${blocked ? "bg-red-500" : "bg-emerald-500"}`}
            style={{ width: `${risk}%` }}
          />
        </div>
      </div>

      <div className="mt-8 space-y-5">
        <div>
          <p className="text-xs text-slate-500">DETECTION REASON</p>
          <p className="mt-1 text-sm text-slate-200">{result.reason}</p>
        </div>

        {[
          ["Detector", result.detected_by],
          ["Confidence", typeof result.confidence === "number" ? `${(result.confidence * 100).toFixed(1)}%` : "N/A"],
          ["Detection latency", `${result.latency_ms ?? "N/A"} ms`],
          ["Total latency", `${result.total_latency_ms ?? "N/A"} ms`],
          ["Chatbot called", result.chatbot_called ? "Yes" : "No"],
        ].map(([label, value]) => (
          <div key={label} className="flex justify-between gap-3 text-sm">
            <span className="text-slate-400">{label}</span>
            <span className="text-right text-white">{value}</span>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-xl bg-slate-950 p-4 text-sm text-slate-300">
        {blocked
          ? "This prompt was stopped before reaching the chatbot."
          : "This prompt passed security screening."}
      </div>
    </section>
  );
}
