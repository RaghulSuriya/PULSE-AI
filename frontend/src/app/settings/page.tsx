"use client";

import { useEffect, useState } from "react";
import { Settings as SettingsIcon, CheckCircle2, AlertCircle, Smartphone, Mail, Calendar, Cpu, Sparkles, LogIn, LogOut } from "lucide-react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [integrations, setIntegrations] = useState<any>(null);
  const [prefs, setPrefs] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [authUrlLoading, setAuthUrlLoading] = useState(false);

  const fetchStatus = () => {
    setLoading(true);
    Promise.all([api.getIntegrations(), api.getPreferences()])
      .then(([iData, pData]) => {
        setIntegrations(iData);
        setPrefs(pData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleConnectGoogle = async () => {
    setAuthUrlLoading(true);
    try {
      const res = await fetch("/api/v1/auth/login/google/url");
      const data = await res.json();
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } catch (err) {
      console.error("Failed to fetch Google Auth URL", err);
    } finally {
      setAuthUrlLoading(false);
    }
  };

  const handleDisconnectGoogle = async () => {
    try {
      await fetch("/api/v1/auth/disconnect", { method: "POST" });
      fetchStatus();
    } catch (err) {
      console.error("Failed to disconnect Google account", err);
    }
  };

  if (loading) return <div className="py-12 text-center text-gray-400">Loading system settings...</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-indigo-400" />
          System Settings & Environment Status
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          Truthful environment-aware status for authorized digital sources and AI model integrations.
        </p>
      </div>

      {/* Environment Mode Banner */}
      <div className="glass-panel p-4 rounded-xl border border-indigo-500/30 bg-indigo-500/5 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <div>
            <span className="text-xs font-bold text-white uppercase tracking-wider">Active System Mode</span>
            <p className="text-xs text-indigo-200">{integrations?.environment}</p>
          </div>
        </div>
        <span className="text-xs font-mono font-semibold px-3 py-1 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
          HEALTHY
        </span>
      </div>

      {/* Connected Channels & APIs */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white">Digital Source Channel Status</h2>
          {integrations?.google_account?.connected ? (
            <button
              onClick={handleDisconnectGoogle}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-300 border border-rose-500/20 hover:bg-rose-500/20 flex items-center gap-1.5 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" /> Disconnect Google
            </button>
          ) : (
            <button
              onClick={handleConnectGoogle}
              disabled={authUrlLoading}
              className="text-xs font-semibold px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white flex items-center gap-1.5 transition-colors shadow-lg shadow-indigo-600/20"
            >
              <LogIn className="w-3.5 h-3.5" /> {authUrlLoading ? "Connecting..." : "Connect Google Account"}
            </button>
          )}
        </div>

        <div className="space-y-3">
          {/* Google Account */}
          <div className="p-4 rounded-xl bg-surface-card border border-surface-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                <SettingsIcon className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Google Account OAuth</h3>
                <p className="text-xs text-gray-400">{integrations?.google_account?.status}</p>
              </div>
            </div>
            <span className={`text-xs font-semibold px-3 py-1 rounded border flex items-center gap-1 font-mono ${
              integrations?.google_account?.connected
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-amber-500/10 text-amber-300 border-amber-500/20"
            }`}>
              {integrations?.google_account?.connected ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
              {integrations?.google_account?.connected ? "CONNECTED" : "NOT CONNECTED"}
            </span>
          </div>

          {/* Gmail API */}
          <div className="p-4 rounded-xl bg-surface-card border border-surface-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Gmail API Channel</h3>
                <p className="text-xs text-gray-400">{integrations?.gmail?.status}</p>
              </div>
            </div>
            <span className={`text-xs font-semibold px-3 py-1 rounded border flex items-center gap-1 font-mono ${
              integrations?.gmail?.connected
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-amber-500/10 text-amber-300 border-amber-500/20"
            }`}>
              {integrations?.gmail?.connected ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
              {integrations?.gmail?.connected ? "CONNECTED" : "FALLBACK / UNSET"}
            </span>
          </div>

          {/* Google Calendar */}
          <div className="p-4 rounded-xl bg-surface-card border border-surface-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Google Calendar API Channel</h3>
                <p className="text-xs text-gray-400">{integrations?.google_calendar?.status}</p>
              </div>
            </div>
            <span className={`text-xs font-semibold px-3 py-1 rounded border flex items-center gap-1 font-mono ${
              integrations?.google_calendar?.connected
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-amber-500/10 text-amber-300 border-amber-500/20"
            }`}>
              {integrations?.google_calendar?.connected ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
              {integrations?.google_calendar?.connected ? "CONNECTED" : "FALLBACK / UNSET"}
            </span>
          </div>

          {/* AI Provider */}
          <div className="p-4 rounded-xl bg-surface-card border border-surface-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">AI Provider Engine ({integrations?.ai_provider?.provider})</h3>
                <p className="text-xs text-gray-400">Model: {integrations?.ai_provider?.model} • {integrations?.ai_provider?.status}</p>
              </div>
            </div>
            <span className="text-xs font-semibold px-3 py-1 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 font-mono">
              {integrations?.ai_provider?.status}
            </span>
          </div>

          {/* Android Companion */}
          <div className="p-4 rounded-xl bg-surface-card border border-surface-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Smartphone className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Android Notification Companion</h3>
                <p className="text-xs text-gray-400">{integrations?.mobile_companion?.status}</p>
              </div>
            </div>
            <span className={`text-xs font-semibold px-3 py-1 rounded border flex items-center gap-1 font-mono ${
              integrations?.mobile_companion?.connected
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-gray-500/10 text-gray-400 border-gray-500/20"
            }`}>
              {integrations?.mobile_companion?.connected ? "LINKED" : "NOT CONNECTED"}
            </span>
          </div>
        </div>
      </div>

      {/* User Preferences */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="text-base font-bold text-white">Attention Schedule Working Hours</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-surface-card border border-surface-border space-y-1">
            <label className="text-gray-400 font-semibold">Work Window Start Time</label>
            <input
              type="text"
              defaultValue={prefs?.work_start_time || "08:30"}
              className="w-full bg-surface/80 border border-surface-border rounded p-2 text-white font-mono"
            />
          </div>
          <div className="p-4 rounded-xl bg-surface-card border border-surface-border space-y-1">
            <label className="text-gray-400 font-semibold">Work Window End Time</label>
            <input
              type="text"
              defaultValue={prefs?.work_end_time || "18:30"}
              className="w-full bg-surface/80 border border-surface-border rounded p-2 text-white font-mono"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

