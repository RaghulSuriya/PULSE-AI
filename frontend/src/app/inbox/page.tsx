"use client";

import { useEffect, useState } from "react";
import { Inbox as InboxIcon, HelpCircle, CheckCircle2, ShieldAlert, Sparkles, Filter, Mail, MessageSquare } from "lucide-react";
import { ExplainabilityModal } from "@/components/explainability_modal";
import { api } from "@/lib/api";
import { EmailMessage, NotificationItem } from "@/types";

export default function InboxPage() {
  const [emails, setEmails] = useState<EmailMessage[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [activeTab, setActiveTab] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);
  const [modalEntity, setModalEntity] = useState<{ id: string; type: string; title: string } | null>(null);

  useEffect(() => {
    Promise.all([api.getEmails(), api.getNotifications()])
      .then(([emailRes, notifRes]) => {
        setEmails(emailRes);
        setNotifications(notifRes);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const allItems = [
    ...emails.map(e => ({
      id: e.id,
      source: "GMAIL",
      sender: e.sender,
      title: e.subject,
      snippet: e.snippet,
      classification: e.classification,
      confidence: e.confidence,
      reasoning: e.reasoning,
      received_at: e.received_at
    })),
    ...notifications.map(n => ({
      id: n.id,
      source: n.source_app,
      sender: n.source_app,
      title: n.title || n.content,
      snippet: n.content,
      classification: n.classification,
      confidence: n.confidence,
      reasoning: n.reasoning,
      received_at: n.timestamp
    }))
  ];

  const filteredItems = allItems.filter(item => {
    if (activeTab === "ALL") return true;
    if (activeTab === "ACTION_REQUIRED") return item.classification === "ACTION_REQUIRED";
    if (activeTab === "INFORMATION") return item.classification === "INFORMATION_ONLY";
    if (activeTab === "PROMOTIONS") return item.classification === "PROMOTIONAL";
    if (activeTab === "IGNORED") return item.classification === "IRRELEVANT";
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <InboxIcon className="w-6 h-6 text-indigo-400" />
            Unified Attention Inbox
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            AI automatically filters noise, detects actionable deadlines, and extracts tasks.
          </p>
        </div>
      </div>

      {/* Tabs Filter */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-3">
        {["ALL", "ACTION_REQUIRED", "INFORMATION", "PROMOTIONS", "IGNORED"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === tab
                ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 shadow-lg"
                : "text-gray-400 hover:text-white hover:bg-white/5"
            }`}
          >
            {tab.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Feed List */}
      <div className="space-y-3">
        {loading ? (
          <div className="py-12 text-center text-gray-400 text-sm">Analyzing digital sources...</div>
        ) : filteredItems.length === 0 ? (
          <div className="py-12 text-center text-gray-400 text-sm">No communications found in this filter category.</div>
        ) : (
          filteredItems.map((item) => (
            <div key={item.id} className="glass-card-interactive p-5 rounded-2xl border border-surface-border space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                    {item.source === "GMAIL" ? <Mail className="w-4 h-4" /> : <MessageSquare className="w-4 h-4" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white">{item.sender}</span>
                      <span className="text-[10px] text-gray-400 font-mono">({item.source})</span>
                    </div>
                    <h3 className="text-sm font-semibold text-gray-200 mt-0.5">{item.title}</h3>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold px-2.5 py-1 rounded font-mono uppercase ${
                    item.classification === "ACTION_REQUIRED"
                      ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                      : item.classification === "PROMOTIONAL"
                      ? "bg-amber-500/20 text-amber-300"
                      : "bg-gray-500/20 text-gray-300"
                  }`}>
                    {item.classification}
                  </span>

                  <button
                    onClick={() => setModalEntity({ id: item.id, type: "CLASSIFICATION", title: item.title })}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-indigo-300 hover:bg-white/10 transition-all"
                    title="Why did PULSE select this?"
                  >
                    <HelpCircle className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <p className="text-xs text-gray-300 leading-relaxed pl-11">{item.snippet}</p>

              {/* AI Reasoning Pill */}
              <div className="pl-11 pt-2 border-t border-white/5 flex items-center justify-between text-[11px] text-gray-400">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span>AI Confidence: <strong className="text-emerald-400">{Math.round(item.confidence * 100)}%</strong></span>
                  <span className="text-gray-500">•</span>
                  <span className="truncate">{item.reasoning[0]}</span>
                </div>
                <span className="text-gray-500 font-mono text-[10px]">
                  {new Date(item.received_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))
        )}
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
