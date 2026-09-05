"use client";

import { useState } from "react";
import { Sparkles, Send, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

interface NLInputProps {
  onSuccess?: () => void;
}

export function NLInput({ onSuccess }: NLInputProps) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || loading) return;

    setLoading(true);
    setResultMessage(null);

    try {
      const res = await api.processNLI(text);
      let msg = `AI understood intent: ${res.intent}. `;
      if (res.intent === "REPLAN_DAY") {
        msg += "Dynamic day replan executed.";
      } else {
        msg += `Created item '${res.title}' (${res.duration_minutes}m duration).`;
      }
      setResultMessage(msg);
      setText("");
      if (onSuccess) onSuccess();
    } catch (err) {
      setResultMessage("Failed to parse natural language input. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="absolute left-4 text-indigo-400">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Instruct PULSE in plain english (e.g. 'Study AWS tomorrow for 2 hours' or 'I couldn't finish my assignment today')..."
          className="w-full pl-12 pr-28 py-3.5 rounded-xl bg-surface-card/80 border border-surface-border text-sm text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 shadow-xl transition-all"
        />
        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="absolute right-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          Instruct
        </button>
      </form>

      {resultMessage && (
        <div className="mt-2 text-xs font-medium px-4 py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 flex items-center justify-between">
          <span>{resultMessage}</span>
          <button onClick={() => setResultMessage(null)} className="text-gray-400 hover:text-white">×</button>
        </div>
      )}
    </div>
  );
}
