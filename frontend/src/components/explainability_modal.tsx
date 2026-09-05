"use client";

import { useEffect, useState } from "react";
import { HelpCircle, CheckCircle2, ShieldAlert, Cpu, X, FileText } from "lucide-react";
import { api } from "@/lib/api";

interface ExplainabilityModalProps {
  isOpen: boolean;
  onClose: () => void;
  entityType: string;
  entityId: string;
  title: string;
}

export function ExplainabilityModal({
  isOpen,
  onClose,
  entityType,
  entityId,
  title,
}: ExplainabilityModalProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen && entityId) {
      setLoading(true);
      api.explainDecision(entityType, entityId)
        .then((res) => setData(res))
        .catch(() => setData(null))
        .finally(() => setLoading(false));
    }
  }, [isOpen, entityType, entityId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-white/10 shadow-2xl relative animate-in fade-in zoom-in duration-200">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono font-semibold uppercase px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              EXPLAINABLE AI RATIONALE
            </span>
            <h3 className="text-base font-bold text-white mt-1">{title}</h3>
          </div>
        </div>

        {loading ? (
          <div className="py-8 text-center text-gray-400 text-sm">Evaluating decision trace...</div>
        ) : (
          <div className="space-y-4 text-sm">
            {/* Primary Explanation */}
            <div className="p-4 rounded-xl bg-surface-card border border-surface-border">
              <h4 className="text-xs font-semibold text-gray-300 mb-1 flex items-center gap-1.5">
                <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
                Why did PULSE select and prioritize this?
              </h4>
              <p className="text-gray-200 text-xs leading-relaxed">{data?.explanation}</p>
            </div>

            {/* Confidence Score Bar */}
            <div className="p-4 rounded-xl bg-surface-card border border-surface-border space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400 font-medium">AI Confidence Score</span>
                <span className="font-bold text-emerald-400 font-mono">
                  {Math.round((data?.confidence || 0.96) * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-700/50 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-2 rounded-full"
                  style={{ width: `${(data?.confidence || 0.96) * 100}%` }}
                />
              </div>
            </div>

            {/* Applied Heuristics & Rules */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Applied Rules & Constraints</h4>
              <div className="space-y-1.5">
                {(data?.applied_rules || []).map((rule: string, idx: number) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-gray-300 p-2.5 rounded-lg bg-white/5 border border-white/5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{rule}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2 text-right">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
              >
                Close Audit View
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
