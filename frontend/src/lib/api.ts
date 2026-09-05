const getApiBase = () => {
  if (typeof window !== "undefined" && process.env.NEXT_PUBLIC_API_URL) {
    const raw = process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "");
    return raw.endsWith("/api/v1") ? raw : `${raw}/api/v1`;
  }
  return "/api/v1";
};

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const apiBase = getApiBase();
  try {
    const res = await fetch(`${apiBase}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`Fetch error for ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // User & Auth
  getMe: () => fetchAPI<any>("/auth/me"),
  getPreferences: () => fetchAPI<any>("/users/me/preferences"),
  
  // Plans & Schedule
  getTodayPlan: () => fetchAPI<any>("/plans/today"),
  replanDay: (reason?: string) => fetchAPI<any>("/plans/replan", { method: "POST", body: JSON.stringify({ reason }) }),
  getPlanVersions: () => fetchAPI<any>("/plans/versions"),

  // Tasks
  getTasks: (status?: string, category?: string) => {
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    if (category) params.append("category", category);
    return fetchAPI<any[]>(`/tasks?${params.toString()}`);
  },
  createTask: (data: any) => fetchAPI<any>("/tasks", { method: "POST", body: JSON.stringify(data) }),
  updateTask: (id: string, data: any) => fetchAPI<any>(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteTask: (id: string) => fetchAPI<any>(`/tasks/${id}`, { method: "DELETE" }),
  completeTask: (id: string, actual_minutes: number) => fetchAPI<any>(`/tasks/${id}/complete`, { method: "POST", body: JSON.stringify({ actual_duration_minutes: actual_minutes }) }),


  // Communications & Notifications
  getEmails: () => fetchAPI<any[]>("/gmail/messages"),
  getNotifications: () => fetchAPI<any[]>("/mobile/notifications"),

  // AI & NLI
  processNLI: (text: string) => fetchAPI<any>("/ai/nli", { method: "POST", body: JSON.stringify({ text }) }),
  explainDecision: (type: string, id: string) => fetchAPI<any>(`/ai/explain/${type}/${id}`),

  // News & Insights
  getNews: (category?: string) => fetchAPI<any[]>(`/news${category ? `?category=${encodeURIComponent(category)}` : ""}`),
  getInsights: () => fetchAPI<any>("/insights"),
  getAuditLogs: () => fetchAPI<any[]>("/audit/logs"),
  getIntegrations: () => fetchAPI<any>("/settings/integrations"),
};
