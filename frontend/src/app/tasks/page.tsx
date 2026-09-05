"use client";

import { useEffect, useState } from "react";
import { CheckSquare, Plus, Clock, AlertCircle, CheckCircle2, Pencil, Trash2, X, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { TaskItem } from "@/types";

export default function TasksPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>("ALL");

  // Modal & Form State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskItem | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  // Form Fields
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("GENERAL");
  const [priority, setPriority] = useState("SHOULD_DO");
  const [deadline, setDeadline] = useState("");
  const [estimatedDuration, setEstimatedDuration] = useState(30);
  const [consequence, setConsequence] = useState("");

  const loadTasks = () => {
    setLoading(true);
    setError(null);
    api.getTasks()
      .then(setTasks)
      .catch((err) => {
        console.error(err);
        setError("Failed to load tasks from server.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const openCreateModal = () => {
    setEditingTask(null);
    setTitle("");
    setDescription("");
    setCategory("GENERAL");
    setPriority("SHOULD_DO");
    setDeadline("");
    setEstimatedDuration(30);
    setConsequence("");
    setIsModalOpen(true);
  };

  const openEditModal = (task: TaskItem) => {
    setEditingTask(task);
    setTitle(task.title || "");
    setDescription(task.description || "");
    setCategory(task.category || "GENERAL");
    setPriority(task.priority || "SHOULD_DO");
    
    // Format deadline for datetime-local input
    if (task.deadline) {
      const d = new Date(task.deadline);
      const isoLocal = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
      setDeadline(isoLocal);
    } else {
      setDeadline("");
    }
    
    setEstimatedDuration(task.estimated_duration || 30);
    setConsequence(task.consequence || "");
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setSubmitting(true);
    setError(null);

    const payload = {
      title: title.trim(),
      description: description.trim() || undefined,
      category,
      priority,
      deadline: deadline ? new Date(deadline).toISOString() : undefined,
      estimated_duration: Number(estimatedDuration) || 30,
      consequence: consequence.trim() || undefined,
      source: editingTask ? editingTask.source : "USER_CREATED",
    };

    try {
      if (editingTask) {
        await api.updateTask(editingTask.id, payload);
      } else {
        await api.createTask(payload);
      }
      setIsModalOpen(false);
      loadTasks();
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to save task. Please check server logs.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    setSubmitting(true);
    setError(null);
    try {
      await api.deleteTask(id);
      setDeleteConfirmId(null);
      loadTasks();
    } catch (err: any) {
      console.error(err);
      setError("Failed to delete task.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleComplete = async (id: string) => {
    try {
      await api.completeTask(id, 30);
      loadTasks();
    } catch (err: any) {
      console.error(err);
      setError("Failed to complete task.");
    }
  };

  const filteredTasks = tasks.filter(t => filterCategory === "ALL" || t.category === filterCategory);

  return (
    <div className="space-y-6">
      {/* Header & Create Task Action */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <CheckSquare className="w-6 h-6 text-indigo-400" />
            Unified Task Matrix
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Tasks auto-generated from Emails, SMS, Documents, and Manual Commands with estimated effort.
          </p>
        </div>

        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-all shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4" />
          Create Task
        </button>
      </div>

      {/* Error Notification */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
          <span className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400" />
            {error}
          </span>
          <button onClick={() => setError(null)} className="text-rose-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-3 overflow-x-auto">
        {["ALL", "COLLEGE", "WORK", "BILLS", "PERSONAL", "GENERAL"].map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all shrink-0 ${
              filterCategory === cat
                ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 shadow-lg"
                : "text-gray-400 hover:text-white hover:bg-white/5"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Task Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-2 py-12 text-center text-gray-400 text-sm">Loading task matrix...</div>
        ) : filteredTasks.length === 0 ? (
          <div className="col-span-2 py-12 text-center text-gray-500 text-sm glass-panel rounded-2xl border border-white/5">
            No tasks found in category '{filterCategory}'. Click "+ Create Task" to add one.
          </div>
        ) : (
          filteredTasks.map((task) => (
            <div key={task.id} className="glass-card-interactive p-5 rounded-2xl border border-surface-border space-y-3 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                      {task.category} • {task.source}
                    </span>
                    <h3 className="text-base font-bold text-white mt-1.5">{task.title}</h3>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                      task.priority === "MUST_DO"
                        ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                        : task.priority === "SHOULD_DO"
                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                        : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                    }`}>
                      {task.priority}
                    </span>

                    {/* Edit Action */}
                    <button
                      onClick={() => openEditModal(task)}
                      title="Edit task"
                      className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
                    >
                      <Pencil className="w-3.5 h-3.5" />
                    </button>

                    {/* Delete Action */}
                    <button
                      onClick={() => setDeleteConfirmId(task.id)}
                      title="Delete task"
                      className="p-1 rounded-lg text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {task.description && (
                  <p className="text-xs text-gray-300">{task.description}</p>
                )}

                {task.consequence && (
                  <p className="text-[11px] text-rose-300 bg-rose-500/10 p-2 rounded border border-rose-500/20">
                    ⚠️ Consequence: {task.consequence}
                  </p>
                )}

                {task.deadline && (
                  <p className="text-[11px] text-indigo-300 bg-indigo-500/10 p-1.5 rounded font-mono">
                    📅 Deadline: {new Date(task.deadline).toLocaleString()}
                  </p>
                )}
              </div>

              {/* Bottom Metadata & Mark Done */}
              <div className="flex items-center justify-between pt-3 border-t border-white/5 text-xs text-gray-400 mt-2">
                <span className="flex items-center gap-1 font-mono">
                  <Clock className="w-3.5 h-3.5 text-indigo-400" />
                  Est: {task.estimated_duration}m
                </span>

                {task.status !== "COMPLETED" ? (
                  <button
                    onClick={() => handleComplete(task.id)}
                    className="px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/30 text-emerald-300 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Mark Done
                  </button>
                ) : (
                  <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1 font-mono">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Completed ({task.actual_duration || task.estimated_duration}m)
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create / Edit Modal Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="glass-panel w-full max-w-lg p-6 rounded-2xl border border-white/10 space-y-4 shadow-2xl bg-surface/95">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                {editingTask ? "Edit Task" : "Create New Task"}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              {/* Title */}
              <div className="space-y-1">
                <label className="text-gray-300 font-semibold">Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Study AWS Architecture for 2 hours"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-surface-card border border-surface-border rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Description */}
              <div className="space-y-1">
                <label className="text-gray-300 font-semibold">Description</label>
                <textarea
                  rows={2}
                  placeholder="Detailed notes or subtask description..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-surface-card border border-surface-border rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Category & Priority */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-gray-300 font-semibold">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-surface-card border border-surface-border rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="GENERAL">GENERAL</option>
                    <option value="COLLEGE">COLLEGE</option>
                    <option value="WORK">WORK</option>
                    <option value="BILLS">BILLS</option>
                    <option value="PERSONAL">PERSONAL</option>
                    <option value="OPPORTUNITY">OPPORTUNITY</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-gray-300 font-semibold">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full bg-surface-card border border-surface-border rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="MUST_DO">MUST_DO (Urgent / Hard Deadline)</option>
                    <option value="SHOULD_DO">SHOULD_DO (Important)</option>
                    <option value="CAN_MOVE">CAN_MOVE (Flexible)</option>
                    <option value="OPTIONAL">OPTIONAL (Low priority)</option>
                  </select>
                </div>
              </div>

              {/* Deadline & Estimated Duration */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-gray-300 font-semibold">Due Date / Deadline</label>
                  <input
                    type="datetime-local"
                    value={deadline}
                    onChange={(e) => setDeadline(e.target.value)}
                    className="w-full bg-surface-card border border-surface-border rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-gray-300 font-semibold">Estimated Duration (Mins)</label>
                  <input
                    type="number"
                    min={5}
                    step={5}
                    value={estimatedDuration}
                    onChange={(e) => setEstimatedDuration(Number(e.target.value))}
                    className="w-full bg-surface-card border border-surface-border rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>
              </div>

              {/* Consequence / Penalty */}
              <div className="space-y-1">
                <label className="text-gray-300 font-semibold">Risk / Consequence of Missed Task</label>
                <input
                  type="text"
                  placeholder="e.g. Disqualification from placement cycle or late fee surcharge"
                  value={consequence}
                  onChange={(e) => setConsequence(e.target.value)}
                  className="w-full bg-surface-card border border-surface-border rounded-xl p-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Modal Actions */}
              <div className="flex items-center justify-end gap-2 pt-3 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-colors font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition-all flex items-center gap-1.5"
                >
                  {submitting ? "Saving..." : editingTask ? "Save Changes" : "Create Task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="glass-panel w-full max-w-sm p-6 rounded-2xl border border-rose-500/20 space-y-4 text-center bg-surface/95">
            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mx-auto">
              <Trash2 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Delete Task?</h3>
            <p className="text-xs text-gray-400">
              Are you sure you want to delete this task? This action will remove the task and trigger dynamic replanning.
            </p>
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirmId)}
                disabled={submitting}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/20 transition-all"
              >
                {submitting ? "Deleting..." : "Confirm Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
