
import { ShieldCheck, Activity } from "lucide-react";

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between border-b border-slate-800 bg-slate-950 px-6 py-4">
      <div className="flex items-center gap-3">
        <ShieldCheck className="h-8 w-8 text-cyan-400" />
        <div>
          <h1 className="text-xl font-bold text-white">
            PromptShield <span className="text-cyan-400">AI</span>
          </h1>
          <p className="text-xs text-slate-400">AI Security Gateway</p>
        </div>
      </div>
      <div className="flex items-center gap-2 text-sm text-emerald-400">
        <Activity className="h-4 w-4" />
        Gateway Dashboard
      </div>
    </nav>
  );
}
