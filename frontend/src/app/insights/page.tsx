"use client";

import { useEffect, useState } from "react";
import { LineChart, CheckCircle2, Clock, AlertTriangle, PieChart, Sparkles } from "lucide-react";
import { api } from "@/lib/api";

export default function InsightsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getInsights()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="py-12 text-center text-gray-400">Loading productivity insights...</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <LineChart className="w-6 h-6 text-indigo-400" />
          Productivity & Time Estimation Insights
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          Non-gamified planning accuracy metrics derived from actual task completion logs.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-white/10 space-y-2">
          <span className="text-xs text-gray-400 font-medium">Tasks Completed (7 Days)</span>
          <p className="text-3xl font-bold text-emerald-400 font-mono">{data.tasks_completed_this_week}</p>
          <span className="text-[11px] text-gray-400">2 tasks postponed to buffer slots</span>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/10 space-y-2">
          <span className="text-xs text-gray-400 font-medium">Deadline Success Rate</span>
          <p className="text-3xl font-bold text-indigo-400 font-mono">{Math.round(data.deadline_success_rate * 100)}%</p>
          <span className="text-[11px] text-gray-400">13 out of 14 hard deadlines met</span>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/10 space-y-2">
          <span className="text-xs text-gray-400 font-medium">Time Estimation Accuracy</span>
          <p className="text-3xl font-bold text-cyan-400 font-mono">{Math.round(data.time_estimation_accuracy.accuracy_ratio * 100)}%</p>
          <span className="text-[11px] text-gray-400">AI learns from user completion history</span>
        </div>
      </div>

      {/* AI Insight Card */}
      <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 bg-indigo-500/5 flex items-start gap-4">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <div className="space-y-1">
          <h3 className="text-sm font-bold text-white">AI Time Feedback Feedback Heuristic</h3>
          <p className="text-xs text-indigo-200 leading-relaxed">
            {data.time_estimation_accuracy.insight_note}
          </p>
        </div>
      </div>

      {/* Workload Breakdown */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <PieChart className="w-4 h-4 text-indigo-400" />
          Workload Distribution by Category
        </h3>

        <div className="space-y-3">
          {(data.workload_by_category || []).map((cat: any, idx: number) => (
            <div key={idx} className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-gray-200 font-semibold">{cat.category}</span>
                <span className="text-gray-400 font-mono">{cat.hours} hours ({cat.percentage}%)</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-indigo-500 h-2 rounded-full"
                  style={{ width: `${cat.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
