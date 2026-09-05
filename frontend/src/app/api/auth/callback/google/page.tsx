"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"processing" | "success" | "error">("processing");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    const code = searchParams.get("code");
    const error = searchParams.get("error");

    if (error) {
      setStatus("error");
      setErrorMsg(`Google OAuth returned error: ${error}`);
      return;
    }

    if (!code) {
      setStatus("error");
      setErrorMsg("No authorization code provided in Google callback.");
      return;
    }

    // Exchange code with backend API
    fetch("/api/v1/auth/login/google", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, redirect_uri: window.location.origin + window.location.pathname }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || "Failed to exchange OAuth authorization code with backend");
        }
        return res.json();
      })
      .then((data) => {
        setStatus("success");
        if (data.access_token) {
          localStorage.setItem("pulse_token", data.access_token);
        }
        setTimeout(() => {
          router.push("/settings");
        }, 1500);
      })
      .catch((err) => {
        setStatus("error");
        setErrorMsg(err.message || "An unexpected error occurred during Google authentication.");
      });
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface p-6">
      <div className="glass-panel max-w-md w-full p-8 rounded-2xl border border-white/10 text-center space-y-4">
        {status === "processing" && (
          <>
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto animate-pulse">
              <Sparkles className="w-6 h-6 animate-spin" />
            </div>
            <h1 className="text-xl font-bold text-white">Completing Google Authentication</h1>
            <p className="text-xs text-gray-400">
              Securing credentials and establishing channel connection with PULSE AI...
            </p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h1 className="text-xl font-bold text-white">Google OAuth Successful</h1>
            <p className="text-xs text-emerald-400">
              Your Google Account, Gmail, and Google Calendar channels are now active! Redirecting to Settings...
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mx-auto">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h1 className="text-xl font-bold text-white">Authentication Failed</h1>
            <p className="text-xs text-rose-300">{errorMsg}</p>
            <button
              onClick={() => router.push("/settings")}
              className="mt-4 text-xs font-semibold px-4 py-2 rounded-xl bg-surface-card border border-surface-border text-white hover:bg-white/10"
            >
              Return to Settings
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-gray-400">Processing authentication...</div>}>
      <CallbackContent />
    </Suspense>
  );
}

