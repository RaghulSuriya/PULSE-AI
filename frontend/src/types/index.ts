export interface UserPreferences {
  occupation: string;
  work_start_time: string;
  work_end_time: string;
  sleep_start_time: string;
  wake_time: string;
  preferred_focus_duration: number;
  buffer_duration_between_tasks: number;
  notification_channels: Record<string, boolean>;
  news_categories: string[];
  demo_mode: boolean;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  picture: string | null;
  is_active: boolean;
  preferences?: UserPreferences;
}

export interface TaskItem {
  id: string;
  user_id: string;
  source: 'EMAIL' | 'SMS' | 'NOTIFICATION' | 'DOCUMENT' | 'CALENDAR' | 'MANUAL_INPUT' | 'USER_CREATED' | 'RECURRING_TASK';
  source_reference?: string;
  title: string;
  description?: string;
  category: 'COLLEGE' | 'WORK' | 'BILLS' | 'PERSONAL' | 'OPPORTUNITY' | 'GENERAL';
  priority: 'MUST_DO' | 'SHOULD_DO' | 'CAN_MOVE' | 'OPTIONAL';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED' | 'POSTPONED';
  deadline?: string;
  estimated_duration: number;
  actual_duration?: number;
  confidence: number;
  consequence?: string;
  explanation?: string;
  created_at: string;
  completed_at?: string;
  dependency_ids?: string[];
}

export interface PlanItem {
  id: string;
  task_id?: string;
  calendar_event_id?: string;
  title: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  item_type: 'TASK' | 'FIXED_EVENT' | 'BUFFER' | 'ROUTINE';
  status: 'SCHEDULED' | 'COMPLETED' | 'SKIPPED' | 'MOVED';
  reason?: string;
}

export interface DailyPlan {
  id: string;
  user_id: string;
  date: string;
  version: number;
  is_active: boolean;
  available_minutes: number;
  fixed_minutes: number;
  planned_workload_minutes: number;
  overload_minutes: number;
  is_overloaded: boolean;
  summary_explanation?: string;
  items: PlanItem[];
  created_at: string;
}

export interface PlanVersion {
  id: string;
  version_number: number;
  trigger_reason: string;
  changes_summary: string[];
  snapshot_items: any[];
  created_at: string;
}

export interface EmailMessage {
  id: string;
  message_id: string;
  sender: string;
  subject: string;
  snippet: string;
  received_at: string;
  classification: 'ACTION_REQUIRED' | 'INFORMATION_ONLY' | 'PROMOTIONAL' | 'IRRELEVANT' | 'UNCERTAIN';
  confidence: number;
  reasoning: string[];
  processed: boolean;
}

export interface NotificationItem {
  id: string;
  source_app: string;
  title?: string;
  content: string;
  timestamp: string;
  classification: string;
  confidence: number;
  reasoning: string[];
  processed: boolean;
}

export interface NewsItem {
  id: string;
  title: string;
  category: string;
  summary: string;
  source: string;
  published_at: string;
  url: string;
  importance: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface AuditLog {
  id: string;
  action_type: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  description: string;
  verified_status: 'PENDING' | 'SUCCESS' | 'FAILED';
  verification_details?: string;
  created_at: string;
}
