"use client";

import { useEffect, useState } from "react";
import { 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  Calendar, 
  HelpCircle, 
  RefreshCw, 
  ArrowRight, 
  ShieldAlert,
  Zap
} from "lucide-react";
import { NLInput } from "@/components/nl_input";
import { ExplainabilityModal } from "@/components/explainability_modal";
import { api } from "@/lib/api";
import { DailyPlan, TaskItem } from "@/types";

export default function DashboardPage() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [replanning, setReplanning] = useState(false);
  const [modalEntity, setModalEntity] = useState<{ id: string; type: string; title: string } | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [planData, tasksData] = await Promise.all([
        api.getTodayPlan(),
        api.getTasks("PENDING")
      ]);
      setPlan(planData);
      setTasks(tasksData);
    } catch (e) {
      console.error(e);
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
      const newPlan = await api.replanDay("Manual dashboard refresh trigger");
      setPlan(newPlan);
    } catch (e) {
      console.error(e);
    } finally {
      setReplanning(false);
    }
  };

  const handleCompleteTask = async (taskId: string) => {
    try {
      await api.completeTask(taskId, 30);
      loadData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Banner: Greeting & Quick NL Input */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-white/10 relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-indigo-600/10 rounded-full blur-3xl" />
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold tracking-wider uppercase">
            <Calendar className="w-3.5 h-3.5" />
            {new Date().toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" })}
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Good morning, Alex 👋</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Your day is <span className="text-emerald-400 font-semibold">82% planned</span> with 0 schedule conflicts.
          </p>
        </div>

        <button
          onClick={handleReplan}
          disabled={replanning}
          className="px-4 py-2.5 rounded-xl bg-surface-card hover:bg-surface-border border border-surface-border text-xs font-semibold text-gray-200 flex items-center gap-2 transition-all self-start md:self-auto shadow-md"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${replanning ? "animate-spin" : ""}`} />
          {replanning ? "Replanning..." : "Replan My Day"}
        </button>
      </div>

      {/* Natural Language Command Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-white/10">
        <NLInput onSuccess={loadData} />
      </div>

      {/* Attention Budget Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400 font-medium">
            <span>Available Focus Time</span>
            <Clock className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-white font-mono">
            {Math.floor((plan?.available_minutes || 480) / 60)}h {(plan?.available_minutes || 480) % 60}m
          </p>
          <span className="text-[11px] text-gray-400">Configured Work Window (08:30 - 18:30)</span>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400 font-medium">
            <span>Fixed Commitments</span>
            <Calendar className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-cyan-400 font-mono">
            {Math.floor((plan?.fixed_minutes || 150) / 60)}h {(plan?.fixed_minutes || 150) % 60}m
          </p>
          <span className="text-[11px] text-gray-400">Google Calendar Events</span>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-xs text-gray-400 font-medium">
            <span>Planned Workload</span>
            <Zap className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-indigo-400 font-mono">
            {Math.floor((plan?.planned_workload_minutes || 215) / 60)}h {(plan?.planned_workload_minutes || 215) % 60}m
          </p>
          <span className="text-[11px] text-gray-400">4 Actionable Items Scheduled</span>
        </div>

        <div className={`glass-panel p-5 rounded-xl border space-y-2 ${plan?.is_overloaded ? "border-rose-500/40 bg-rose-500/10" : "border-emerald-500/30 bg-emerald-500/5"}`}>
          <div className="flex items-center justify-between text-xs font-medium">
            <span className={plan?.is_overloaded ? "text-rose-400" : "text-emerald-400"}>Attention Capacity</span>
            {plan?.is_overloaded ? <AlertTriangle className="w-4 h-4 text-rose-400" /> : <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
          </div>
          <p className={`text-2xl font-bold font-mono ${plan?.is_overloaded ? "text-rose-400" : "text-emerald-400"}`}>
            {plan?.is_overloaded ? `+${plan.overload_minutes}m Over` : "Balanced"}
          </p>
          <span className="text-[11px] text-gray-400">
            {plan?.is_overloaded ? "Day overloaded! Optional tasks moved." : "1h 15m safety buffer remaining"}
          </span>
        </div>
      </div>

      {/* Main Content Layout: Timeline on Left, Action Queue on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Optimized Daily Schedule Timeline */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-indigo-400" />
              Today's Execution Timeline
            </h2>
            <span className="text-xs text-gray-400 font-mono">Plan Version v{plan?.version || 1}</span>
          </div>

          <div className="space-y-3">
            {loading ? (
              <div className="py-12 text-center text-gray-400 text-sm">Building AI daily schedule...</div>
            ) : (plan?.items || []).map((item, idx) => {
              const isFixed = item.item_type === "FIXED_EVENT";

              return (
                <div
                  key={idx}
                  className={`glass-card-interactive p-4 rounded-xl flex items-center justify-between border ${
                    isFixed ? "border-cyan-500/30 bg-cyan-950/20" : "border-surface-border"
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="text-xs font-mono font-bold text-indigo-300 w-24 shrink-0 pt-0.5">
                      {item.start_time} - {item.end_time}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-white">{item.title}</span>
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold uppercase ${
                          isFixed ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30" : "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                        }`}>
                          {item.item_type}
                        </span>
                      </div>

                      {item.reason && (
                        <p className="text-xs text-gray-400 mt-1 line-clamp-1">{item.reason}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setModalEntity({ id: item.id, type: "SCHEDULING", title: item.title })}
                      className="p-1.5 rounded-lg text-gray-400 hover:text-indigo-300 hover:bg-white/5 transition-all"
                      title="Why did PULSE schedule this time?"
                    >
                      <HelpCircle className="w-4 h-4" />
                    </button>
                    {!isFixed && item.task_id && (
                      <button
                        onClick={() => handleCompleteTask(item.task_id!)}
                        className="px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-1 transition-all"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Done
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Action Queue & Approvals Banner */}
        <div className="space-y-6">
          {/* Risk Approval Notice */}
          <div className="glass-panel p-5 rounded-2xl border border-amber-500/30 bg-amber-500/5 space-y-3">
            <div className="flex items-center gap-2 text-amber-400 font-bold text-xs">
              <ShieldAlert className="w-4 h-4" />
              HIGH RISK ACTION APPROVAL REQUIRED
            </div>
            <p className="text-xs text-gray-300">
              PULSE detected an internship application submission draft. Explicit user approval is required before submitting.
            </p>
            <div className="flex gap-2">
              <button className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition-all">
                Approve Submission
              </button>
              <button className="px-3 py-2 bg-white/5 hover:bg-white/10 text-gray-400 rounded-lg text-xs font-semibold">
                Review Draft
              </button>
            </div>
          </div>

          {/* Pending Tasks Queue */}
          <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center justify-between">
              <span>Actionable Queue</span>
              <span className="text-xs font-mono text-indigo-400">{tasks.length} pending</span>
            </h3>

            <div className="space-y-3">
              {tasks.map((task) => (
                <div key={task.id} className="p-3.5 rounded-xl bg-surface-card border border-surface-border space-y-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-xs font-semibold text-white block">{task.title}</span>
                      <span className="text-[10px] text-gray-400 font-mono">{task.source} • {task.estimated_duration}m duration</span>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                      task.priority === "MUST_DO" ? "bg-rose-500/20 text-rose-300 border border-rose-500/30" : "bg-amber-500/20 text-amber-300"
                    }`}>
                      {task.priority}
                    </span>
                  </div>

                  {task.consequence && (
                    <p className="text-[11px] text-rose-300/90 bg-rose-500/10 p-2 rounded border border-rose-500/20 leading-tight">
                      ⚠️ {task.consequence}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Explainability AI Modal */}
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
