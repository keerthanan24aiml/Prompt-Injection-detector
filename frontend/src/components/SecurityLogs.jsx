
import { Clock } from "lucide-react";

export default function SecurityLogs({ logs }) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-5 flex items-center gap-2">
        <Clock className="h-5 w-5 text-cyan-400" />
        <h2 className="text-lg font-bold text-white">Recent Security Logs</h2>
      </div>

      {logs.length === 0 ? (
        <p className="text-sm text-slate-500">No prompts scanned yet.</p>
      ) : (
        <div className="space-y-3">
          {logs.map((log) => (
            <div key={log.id} className="flex flex-col gap-2 rounded-xl bg-slate-950 p-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <p className="break-words text-sm text-slate-200">{log.message}</p>
                <p className="mt-1 text-xs text-slate-500">{log.time}</p>
              </div>
              <span className={`w-fit rounded-full px-3 py-1 text-xs font-bold ${
                log.decision === "BLOCK"
                  ? "bg-red-500/10 text-red-400"
                  : "bg-emerald-500/10 text-emerald-400"
              }`}>
                {log.decision}
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
