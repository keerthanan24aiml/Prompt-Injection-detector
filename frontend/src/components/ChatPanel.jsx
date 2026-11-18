
import { useState } from "react";
import { Send, Bot, ShieldAlert } from "lucide-react";

export default function ChatPanel({ onResult, onLog }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage(e) {
    e.preventDefault();
    const prompt = message.trim();

    if (!prompt || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: prompt }]);
    setMessage("");
    setLoading(true);
    onResult(null);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: prompt }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Backend request failed");
      }

      onResult(data);
      onLog(prompt, data);

      if (data.decision === "BLOCK") {
        setMessages((prev) => [
          ...prev,
          { role: "system", text: "Blocked! PromptShield detected a suspicious prompt." },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: data.chatbot_response || "No response received." },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "system", text: `Error: ${error.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="flex h-[600px] flex-col rounded-2xl border border-slate-800 bg-slate-900">
      <div className="border-b border-slate-800 p-5">
        <h2 className="text-lg font-bold text-white">Chat with AI</h2>
        <p className="text-sm text-slate-400">Every prompt is security checked.</p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-5">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <Bot className="mb-3 h-12 w-12 text-cyan-400" />
            <p className="text-white">Welcome to PromptShield AI</p>
            <p className="mt-2 text-sm text-slate-400">
              Enter a prompt to begin.
            </p>
          </div>
        )}

        {messages.map((item, index) => (
          <div
            key={index}
            className={`flex ${item.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`max-w-[85%] whitespace-pre-wrap break-words rounded-xl px-4 py-3 text-sm ${
              item.role === "user"
                ? "bg-cyan-600 text-white"
                : item.role === "system"
                ? "bg-red-500/10 text-red-300"
                : "bg-slate-800 text-slate-200"
            }`}>
              {item.role === "system" && <ShieldAlert className="mr-2 inline h-4 w-4" />}
              {item.text}
            </div>
          </div>
        ))}

        {loading && <p className="text-sm text-cyan-400">Scanning prompt...</p>}
      </div>

      <form onSubmit={sendMessage} className="flex gap-3 border-t border-slate-800 p-4">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter your prompt..."
          disabled={loading}
          className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-cyan-500"
        />
        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="rounded-xl bg-cyan-600 px-5 text-white hover:bg-cyan-500 disabled:opacity-50"
        >
          <Send className="h-5 w-5" />
        </button>
      </form>
    </section>
  );
}
