"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Inbox, 
  CalendarDays, 
  CheckSquare, 
  Newspaper, 
  LineChart, 
  Settings, 
  ShieldCheck, 
  Zap,
  Sparkles
} from "lucide-react";

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Inbox", href: "/inbox", icon: Inbox },
  { name: "My Plan", href: "/plan", icon: CalendarDays },
  { name: "Tasks", href: "/tasks", icon: CheckSquare },
  { name: "Daily Brief", href: "/brief", icon: Newspaper },
  { name: "Insights", href: "/insights", icon: LineChart },
  { name: "Settings", href: "/settings", icon: Settings },
  { name: "Privacy Center", href: "/privacy", icon: ShieldCheck },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <aside className="w-64 glass-panel border-r border-white/10 min-h-screen p-4 flex flex-col justify-between fixed top-0 left-0 z-40">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-3 py-4 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-cyan-400 flex items-center justify-center glow-primary">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-wider flex items-center gap-1.5">
              PULSE <span className="text-xs px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">AI</span>
            </h1>
            <p className="text-[11px] text-gray-400 font-medium">Attention-to-Execution</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shadow-lg shadow-indigo-500/10"
                    : "text-gray-400 hover:text-white hover:bg-white/5"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : "text-gray-400"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Demo Mode & Profile Footer */}
      <div className="pt-4 border-t border-white/10 space-y-3">
        <div className="px-3 py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-semibold text-indigo-300">DEMO MODE ACTIVE</span>
          </div>
          <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded font-mono">SEEDED DATA</span>
        </div>

        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5 border border-white/5">
          <img
            src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
            alt="Alex Chen"
            className="w-8 h-8 rounded-full border border-indigo-400/40"
          />
          <div className="truncate">
            <p className="text-xs font-semibold text-white truncate">Alex Chen</p>
            <p className="text-[10px] text-gray-400 truncate">demo@pulse.ai</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
