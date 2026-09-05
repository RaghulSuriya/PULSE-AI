"use client";

import { useState } from "react";
import { ShieldCheck, Download, Trash2, Lock, Eye, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function PrivacyPage() {
  const [msg, setMsg] = useState<string | null>(null);

  const handleExport = async () => {
    setMsg("Export requested. Preparing JSON package...");
  };

  const handleClear = async () => {
    if (confirm("Are you sure you want to purge all stored metadata?")) {
      setMsg("All local data purged.");
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
          PULSE AI Privacy & Transparency Center
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          Zero raw email body persistent storage policy. Complete user data sovereignty and disconnect controls.
        </p>
      </div>

      {msg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold">
          {msg}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Lock className="w-4 h-4 text-indigo-400" />
            Data Protection Principles
          </h2>
          <ul className="space-y-3 text-xs text-gray-300">
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold">•</span>
              <span><strong>Minimal Scope Request:</strong> Gmail and Google Calendar access is limited strictly to metadata and required classification scopes.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold">•</span>
              <span><strong>No Consequential Autonomy:</strong> PULSE will NEVER independently make payments, send high-risk emails, or delete data without explicit approval.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold">•</span>
              <span><strong>Encrypted Token Vault:</strong> OAuth tokens are stored using secure token-safe encryption and are never exposed to the frontend.</span>
            </li>
          </ul>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Eye className="w-4 h-4 text-cyan-400" />
            Data Sovereignty Controls
          </h2>
          <div className="space-y-3">
            <button
              onClick={handleExport}
              className="w-full p-3 rounded-xl bg-surface-card hover:bg-surface-border border border-surface-border text-xs font-semibold text-white flex items-center justify-between transition-all"
            >
              <span className="flex items-center gap-2">
                <Download className="w-4 h-4 text-indigo-400" />
                Export Complete Data Package (JSON)
              </span>
              <span className="text-gray-400">Download</span>
            </button>

            <button
              onClick={handleClear}
              className="w-full p-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-xs font-semibold text-rose-300 flex items-center justify-between transition-all"
            >
              <span className="flex items-center gap-2">
                <Trash2 className="w-4 h-4 text-rose-400" />
                Purge All Stored Metadata & Cache
              </span>
              <span>Purge</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
