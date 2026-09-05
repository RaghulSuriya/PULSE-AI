"use client";

import { useEffect, useState } from "react";
import { CalendarDays, RefreshCw, GitCommit, Clock, HelpCircle, CheckCircle2, AlertTriangle, Layers } from "lucide-react";
import { ExplainabilityModal } from "@/components/explainability_modal";
import { api } from "@/lib/api";
import { DailyPlan, PlanVersion } from "@/types";

export default function PlanPage() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [versions, setVersions] = useState<PlanVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [replanning, setReplanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalEntity, setModalEntity] = useState<{ id: string; type: string; title: string } | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [pData, vData] = await Promise.all([
        api.getTodayPlan(),
        api.getPlanVersions()
      ]);
      setPlan(pData);
      setVersions(vData || []);
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Failed to load plan from server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleReplan = async () => {
    try {
      setReplanning(true);
      setError(null);
      const newPlan = await api.replanDay("User requested full schedule re-optimization");
      setPlan(newPlan);
      const vData = await api.getPlanVersions();
      setVersions(vData || []);
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Failed to replan day.");
    } finally {
      setReplanning(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-white/10">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <CalendarDays className="w-4 h-4" />
            AI Attention-to-Execution Schedule
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Today's Optimized Daily Plan</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Active Version: <span className="text-indigo-300 font-mono font-semibold">Plan v{plan?.version || 1}</span> • Dependency-aware time blocking
          </p>
        </div>

        <button
          onClick={handleReplan}
          disabled={replanning}
          className="px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold flex items-center gap-2 transition-all shadow-lg glow-primary"
        >
          <RefreshCw className={`w-4 h-4 ${replanning ? "animate-spin" : ""}`} />
          {replanning ? "Recalculating..." : "Replan My Day"}
        </button>
      </div>

      {/* Error Notification */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
          <span className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            {error}
          </span>
          <button onClick={loadData} className="px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 rounded text-xs font-semibold">
            Retry
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Timeline View */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-indigo-400" />
            Time Slot Allocations
          </h2>

          <div className="space-y-3">
            {loading ? (
              <div className="py-12 text-center text-gray-400 text-sm">Building AI daily schedule...</div>
            ) : (plan?.items || []).map((item, idx) => (
              <div key={idx} className="glass-card-interactive p-4 rounded-xl flex items-center justify-between border border-surface-border">
                <div className="flex items-center gap-4">
                  <div className="text-xs font-mono font-bold text-indigo-300 w-24 shrink-0">
                    {item.start_time} - {item.end_time}
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">{item.title}</h3>
                    <p className="text-xs text-gray-400 mt-0.5">{item.reason}</p>
                  </div>
                </div>

                <button
                  onClick={() => setModalEntity({ id: item.id, type: "SCHEDULING", title: item.title })}
                  className="p-1.5 rounded-lg text-gray-400 hover:text-indigo-300 hover:bg-white/10 transition-all"
                  title="Why this slot?"
                >
                  <HelpCircle className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Plan Version Diff History Sidebar */}
        <div className="space-y-6">
          <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Plan Version History & Diffs
            </h3>

            <div className="space-y-3">
              {versions.map((ver) => (
                <div key={ver.id} className="p-3.5 rounded-xl bg-surface-card border border-surface-border space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-300 font-mono">Plan v{ver.version_number}</span>
                    <span className="text-[10px] text-gray-400 font-mono">
                      {new Date(ver.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <p className="text-xs font-medium text-gray-200">Trigger: {ver.trigger_reason}</p>

                  <div className="space-y-1 pt-1 border-t border-white/5">
                    {ver.changes_summary.map((change, cIdx) => (
                      <div key={cIdx} className="text-[11px] text-gray-400 flex items-center gap-1.5">
                        <GitCommit className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span>{change}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {modalEntity && (
        <ExplainabilityModal
          isOpen={!!modalEntity}
          onClose={() => setModalEntity(null)}
          entityType={modalEntity.type}
          entityId={modalEntity.id}
          title={modalEntity.title}
        />
      )}
    </div>
  );
}
