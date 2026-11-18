
import { useState } from "react";
import Navbar from "./components/Navbar";
import ChatPanel from "./components/ChatPanel";
import SecurityInspector from "./components/SecurityInspector";
import MetricsCards from "./components/MetricsCards";
import SecurityLogs from "./components/SecurityLogs";

export default function App() {
  const [result, setResult] = useState(null);

  const [metrics, setMetrics] = useState({
    total: 0,
    blocked: 0,
    allowed: 0,
  });

  const [logs, setLogs] = useState([]);

  function handleResult(data) {
    setResult(data);
    if (!data) return;

    setMetrics((prev) => ({
      total: prev.total + 1,
      blocked: prev.blocked + (data.decision === "BLOCK" ? 1 : 0),
      allowed: prev.allowed + (data.decision === "ALLOW" ? 1 : 0),
    }));
  }

  function handleLog(message, data) {
    setLogs((prev) => [
      {
        id: Date.now(),
        message,
        decision: data.decision,
        time: new Date().toLocaleTimeString(),
      },
      ...prev,
    ].slice(0, 10));
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />

      <main className="mx-auto max-w-7xl space-y-6 px-5 py-8">
        <div>
          <h2 className="text-2xl font-bold">Security Dashboard</h2>
          <p className="mt-1 text-sm text-slate-400">
            Monitor and protect your chatbot from prompt injection attacks.
          </p>
        </div>

        <MetricsCards metrics={metrics} />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ChatPanel onResult={handleResult} onLog={handleLog} />
          <SecurityInspector result={result} />
        </div>

        <SecurityLogs logs={logs} />
      </main>
    </div>
  );
}
