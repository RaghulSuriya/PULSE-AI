"use client";

import { useEffect, useState } from "react";
import { Newspaper, ExternalLink, Plus, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { NewsItem } from "@/types";

export default function DailyBriefPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [category, setCategory] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getNews(category === "ALL" ? undefined : category)
      .then(setNews)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [category]);

  const handleAddToPlan = async (item: NewsItem) => {
    await api.processNLI(`Read news article: ${item.title}`);
    alert(`Added '${item.title}' as a flexible reading task in your plan!`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Newspaper className="w-6 h-6 text-indigo-400" />
            Curated Daily Brief
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Real news feed with concise AI summaries, strictly separated from actionable task planning.
          </p>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-3">
        {["ALL", "AI & Technology", "Cloud Computing", "Business", "Science"].map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              category === cat
                ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 shadow-lg"
                : "text-gray-400 hover:text-white hover:bg-white/5"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* News Cards */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-12 text-center text-gray-400 text-sm">Fetching curated news items...</div>
        ) : news.map((item) => (
          <div key={item.id} className="glass-card-interactive p-5 rounded-2xl border border-surface-border space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono font-bold uppercase text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded border border-cyan-500/20">
                  {item.category} • {item.source}
                </span>
                <h3 className="text-base font-bold text-white mt-1.5">{item.title}</h3>
              </div>

              <button
                onClick={() => handleAddToPlan(item)}
                className="px-3 py-1.5 bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 rounded-lg text-xs font-semibold flex items-center gap-1.5 shrink-0"
              >
                <Plus className="w-3.5 h-3.5" />
                Add to Plan
              </button>
            </div>

            <p className="text-xs text-gray-300 leading-relaxed">{item.summary}</p>

            <div className="flex items-center justify-between pt-2 border-t border-white/5 text-[11px] text-gray-400">
              <span className="font-mono">Published {new Date(item.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="text-indigo-400 hover:underline flex items-center gap-1 font-semibold"
              >
                Read Source <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
