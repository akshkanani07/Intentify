"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  Sparkles,
  Copy,
  Check,
  Download,
  Terminal,
  ShieldCheck,
  Cpu,
  Layers,
  Gauge,
  Sliders,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  AlertCircle,
  FileText,
  Zap,
  CheckCircle2,
  BookOpen,
  History,
  Columns,
  Clock,
  Binary,
  Bot,
  X,
  Trash2,
  ThumbsUp,
  ThumbsDown,
  MessageSquarePlus,
  Lightbulb,
} from "lucide-react";

interface QualityBreakdown {
  clarity: number;
  specificity: number;
  context: number;
  constraints: number;
  output_format: number;
  ambiguity_handling: number;
  total: number;
}

interface PenaltyItem {
  code: string;
  name: string;
  penalty: number;
  is_hard_check: boolean;
  reason: string;
}

interface ProcessingMetadata {
  detected_language: string;
  detected_intent: string;
  detected_domain: string;
  processing_time_ms: number;
  model_versions?: Record<string, string>;
  aligned_role?: string;
  original_role?: string;
  intent_confidence?: number;
  target_audience?: string;
  experience_level?: string;
  deliverable?: string;
  task_type?: string;
  risk_level?: string;
  identified_risks?: string[];
  smart_assumptions?: string[];
  writing_style?: string;
  formality_level?: string;
  user_emotion?: string;
  decision_priorities?: string[];
  learned_memories_count?: number;
  engine_mode?: string;
  content_source?: string;
  reviewed?: boolean;
  score_before_cap?: number;
  score_after_cap?: number;
  penalties?: PenaltyItem[];
  cognitive_reasoning?: {
    what_user_wants_to_build?: string;
    what_user_wants_to_learn?: string;
    what_user_wants_to_solve?: string;
    actual_user_goal?: string;
    role_adjustment_rationale?: string;
    summary?: string;
  };
  cognitive_quality?: Record<string, number>;
  dynamic_headings?: string[];
  clarifications?: string[];
}

interface PromptGenerationResponse {
  master_prompt: string;
  assumptions: string[];
  quality_score: number | string;
  improvements: string[];
  clarifications?: string[];
  breakdown?: QualityBreakdown;
  metadata?: ProcessingMetadata;
}

interface HistoryItem {
  id: string;
  timestamp: string;
  role: string;
  detail: string;
  domain: string;
  intent: string;
  score: number;
  result: PromptGenerationResponse;
}

const PRESET_SCENARIOS = [
  {
    title: "Scheduling SaaS (Role Alignment)",
    role: "Senior Cloud Architect",
    detail: "I want to make a scheduling website with automated calendar synchronization and booking workflows",
    language: "English",
    tone: "technical",
    format: "Production-Ready Code",
    domain: "Scheduling SaaS Platform",
  },
  {
    title: "Python Pedagogy (Teacher to Instructor)",
    role: "Teacher",
    detail: "I want to learn Python from scratch through hands-on coding exercises and projects",
    language: "English",
    tone: "authoritative",
    format: "Structured Progressive Curriculum",
    domain: "Programming Education",
  },
  {
    title: "Hospital Management (Doctor to HealthTech Architect)",
    role: "Doctor",
    detail: "Create hospital management software with secure patient records and triage workflows",
    language: "English",
    tone: "technical",
    format: "Production-Ready Code",
    domain: "Healthcare Software",
  },
  {
    title: "Destination Wedding Planner (Gujarati)",
    role: "Luxury Destination Wedding Planner",
    detail: "mare wedding planner mate prompt joiye destination wedding in Udaipur with budget 50 lakh, 3 days multi-cultural ceremonies and 250 guests",
    language: "English",
    tone: "authoritative",
    format: "Event Master Coordination Plan",
    domain: "Hospitality & Event Planning",
  },
];

const POPULAR_ROLES = [
  "Senior Cloud Architect",
  "Senior Full Stack SaaS Architect",
  "Python Instructor",
  "Healthcare Technology Architect",
  "Chief Technology Officer",
  "Event & Wedding Specialist",
];

const OUTPUT_FORMATS = [
  { value: "", label: "Auto-Select Optimal Blueprint" },
  { value: "Production-Ready Code", label: "Production-Ready Code & Architecture" },
  { value: "Structured Progressive Curriculum", label: "Structured Progressive Curriculum" },
  { value: "Event Master Coordination Plan", label: "Event Master Coordination Plan" },
  { value: "Step-by-Step Execution Guide", label: "Step-by-Step Execution Guide" },
  { value: "Executive Briefing Memo", label: "Executive Briefing Memo" },
  { value: "Comprehensive Strategic Blueprint", label: "Comprehensive Strategic Blueprint" },
];

const TONES = [
  { value: "", label: "Calibrated to Intent (Recommended)" },
  { value: "authoritative", label: "Authoritative & Executive" },
  { value: "technical", label: "Technical & Rigorous" },
  { value: "persuasive", label: "Strategic & Persuasive" },
  { value: "concise", label: "Concise & Operational" },
  { value: "creative", label: "Creative & Visionary" },
];

const LANGUAGES = [
  { value: "auto", label: "Auto (matches input language)" },
  { value: "English", label: "English" },
  { value: "Gujarati", label: "ગુજરાતી (Gujarati)" },
  { value: "Hindi", label: "हिन्दी (Hindi)" },
];

const TARGET_LLMS = [
  { value: "universal", label: "Universal Standard (Balanced Markdown)" },
  { value: "claude", label: "Claude 3.5 Sonnet / Opus (XML Artifacts & Rules)" },
  { value: "gpt4", label: "GPT-4o / o1 (System Role Directive & Markdown)" },
  { value: "deepseek", label: "DeepSeek R1 / V3 (Reasoning & Thinking Blocks)" },
  { value: "local_llama", label: "Local Llama 3 / Qwen 2.5 (Concise Instruction Tokens)" },
];

function formatPromptForTarget(prompt: string, target: string, alignedRole?: string): string {
  if (target === "claude") {
    return `<system_instructions>
Adopt the role of ${alignedRole || "Domain Specialist"} with rigorous precision.
Follow all structured sections, acceptance criteria, and constraints defined below.
</system_instructions>

<master_prompt>
${prompt}
</master_prompt>`;
  }
  if (target === "gpt4") {
    return `### SYSTEM ROLE & OPERATIONAL DIRECTIVE
You are an authoritative ${alignedRole || "Expert Architect"}. Comply strictly with all specified constraints, schema contracts, and deliverables without conversational filler.

### MASTER PROMPT
${prompt}`;
  }
  if (target === "deepseek") {
    return `<thinking_framework>
1. Reason carefully through requirements, constraints, and architecture before synthesizing outputs.
2. Verify all mathematical, algorithmic, and domain consistency points.
</thinking_framework>

${prompt}`;
  }
  if (target === "local_llama") {
    return `[INST] <<SYS>>
You are an expert ${alignedRole || "Specialist"}. Execute the following master prompt with zero boilerplate:
<</SYS>>

${prompt} [/INST]`;
  }
  return prompt;
}

export default function IntentifyApp() {
  const [role, setRole] = useState("");
  const [detail, setDetail] = useState("");
  const [language, setLanguage] = useState("auto");
  const [tone, setTone] = useState("");
  const [format, setFormat] = useState("");
  const [targetLLM, setTargetLLM] = useState("universal");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Execution states
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [result, setResult] = useState<PromptGenerationResponse | null>(null);

  // Feedback states
  const [feedbackRating, setFeedbackRating] = useState<"up" | "down" | null>(null);
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackToast, setFeedbackToast] = useState<string | null>(null);

  // Active section filter or tab
  const [activeTab, setActiveTab] = useState<"prompt" | "diff" | "cognitive" | "assumptions" | "quality">("prompt");

  // Load history from localStorage on client mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem("intentify_prompt_history");
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch {
      // ignore localstorage errors
    }
  }, []);

  const saveHistory = useCallback((item: HistoryItem) => {
    setHistory((prev) => {
      const updated = [item, ...prev.filter((p) => p.id !== item.id)].slice(0, 20);
      try {
        localStorage.setItem("intentify_prompt_history", JSON.stringify(updated));
      } catch {
        // ignore
      }
      return updated;
    });
  }, []);

  const clearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem("intentify_prompt_history");
    } catch {
      // ignore
    }
  };

  const loadScenario = (s: (typeof PRESET_SCENARIOS)[0]) => {
    setRole(s.role);
    setDetail(s.detail);
    setLanguage(s.language);
    setTone(s.tone);
    setFormat(s.format);
    setError(null);
  };

  const loadFromHistory = (item: HistoryItem) => {
    setRole(item.role);
    setDetail(item.detail);
    setResult(item.result);
    setActiveTab("prompt");
    setShowHistory(false);
  };

  const handleGenerate = useCallback(async () => {
    if (!detail.trim()) {
      setError("Please enter a task description, requirement, or instruction.");
      return;
    }

    setLoading(true);
    setError(null);
    setFeedbackRating(null);
    setFeedbackToast(null);

    const stages = [
      "1/9 Language & Script Detection (NFC Normalization)...",
      "2/9 15-Intent & 21-Domain Classification...",
      "3/9 Spec Extraction & Product-Name Disentanglement...",
      "4/9 Role-Task Alignment & Persona Validation...",
      "5/9 Grounded Concept Graph & Contract Retrieval...",
      "6/9 Dynamic Grammar-Constrained JSON Synthesis...",
      "7/9 Markdown Composition & Sentence Deduplication...",
      "8/9 S7 Pure Validators & Score Honesty Verification...",
      "9/9 Multi-Candidate Reranker & Master Selection...",
    ];

    let stageIdx = 0;
    const stageInterval = setInterval(() => {
      if (stageIdx < stages.length) {
        setLoadingStage(stages[stageIdx]);
        stageIdx++;
      }
    }, 280);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${apiUrl}/api/v1/generate-prompt`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          role: role.trim(),
          detail: detail.trim(),
          language: language === "auto" ? null : language || null,
          tone: tone || null,
          format: format || null,
        }),
      });

      clearInterval(stageInterval);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData?.detail?.message ||
            errorData?.message ||
            `Server error: ${response.status} ${response.statusText}`
        );
      }

      const data: PromptGenerationResponse = await response.json();
      setResult(data);
      setActiveTab("prompt");

      // Save to local history
      const historyItem: HistoryItem = {
        id: `run-${Date.now()}`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        role: role.trim() || data.metadata?.aligned_role || "Synthesized Specialist",
        detail: detail.trim(),
        domain: data.metadata?.detected_domain || "General",
        intent: data.metadata?.detected_intent || "Task",
        score: typeof data.quality_score === "number" ? data.quality_score : parseFloat(String(data.quality_score || "0")),
        result: data,
      };
      saveHistory(historyItem);
    } catch (err: unknown) {
      clearInterval(stageInterval);
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
        setError(
          "Backend connection failed. Please ensure the backend server is running on http://127.0.0.1:8000 (Run: .\\start-backend.ps1 or run_intentify.bat)"
        );
      } else {
        setError(msg || "Failed to compile prompt. Please check backend logs.");
      }
    } finally {
      setLoading(false);
      setLoadingStage("");
    }
  }, [detail, role, language, tone, format, saveHistory]);

  // Keyboard shortcut: Ctrl+Enter / Cmd+Enter to generate
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        if (detail.trim() && !loading) {
          handleGenerate();
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [detail, loading, handleGenerate]);

  // Formatted master prompt based on Target LLM
  const displayedPrompt = useMemo(() => {
    if (!result?.master_prompt) return "";
    return formatPromptForTarget(result.master_prompt, targetLLM, result.metadata?.aligned_role);
  }, [result, targetLLM]);

  // Live Token & Context Estimator Metrics
  const tokenTelemetry = useMemo(() => {
    if (!displayedPrompt) return null;
    const charCount = displayedPrompt.length;
    const estTokens = Math.ceil(charCount / 4);
    const words = displayedPrompt.trim().split(/\s+/).filter(Boolean).length;
    const estReadingTimeMin = Math.max(1, Math.ceil(words / 220));
    const contextFootprintPercent = ((estTokens / 128000) * 100).toFixed(2);
    return {
      charCount,
      estTokens,
      words,
      estReadingTimeMin,
      contextFootprintPercent,
    };
  }, [displayedPrompt]);

  const handleFeedback = async (ratingType: "up" | "down") => {
    if (!result || feedbackSubmitting) return;
    setFeedbackSubmitting(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const numericRating = ratingType === "up" ? 5 : 2;
      const response = await fetch(`${apiUrl}/api/v1/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt_text: displayedPrompt || result.master_prompt,
          goal: detail.trim(),
          domain: result.metadata?.detected_domain || "",
          rating: numericRating,
          comments: ratingType === "up" ? "Helpful and accurate prompt" : "Needs improvement",
        }),
      });
      if (response.ok) {
        setFeedbackRating(ratingType);
        setFeedbackToast(
          ratingType === "up"
            ? "Saved exemplar to offline learning memory!"
            : "Feedback recorded for offline learning store."
        );
        setTimeout(() => setFeedbackToast(null), 4000);
      }
    } catch (err) {
      console.error("Feedback submission failed:", err);
    } finally {
      setFeedbackSubmitting(false);
    }
  };

  const handleApplyClarification = (clarificationText: string) => {
    setDetail((prev) => {
      const clean = prev.trim();
      return `${clean}\n- Clarification: ${clarificationText}`;
    });
  };

  const handleCopy = () => {
    if (!displayedPrompt) return;
    navigator.clipboard.writeText(displayedPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!displayedPrompt) return;
    const blob = new Blob([displayedPrompt], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `intentify-master-prompt-${targetLLM}-${Date.now()}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleReset = () => {
    setRole("");
    setDetail("");
    setLanguage("auto");
    setTone("");
    setFormat("");
    setTargetLLM("universal");
    setResult(null);
    setError(null);
    setFeedbackRating(null);
    setFeedbackToast(null);
  };

  const promptScoreNumber =
    typeof result?.quality_score === "number"
      ? result.quality_score
      : parseFloat(String(result?.quality_score || "0"));

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30">
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-[#0b1120]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  Intentify AI
                </span>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Universal Compiler v2.5
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">
                Deterministic Cognitive Prompt Compiler &bull; 100% Offline & Local
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <div className="hidden md:flex items-center gap-2 text-xs text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>100% Air-Gapped Local Inference (NumPy + 9 Contracts)</span>
            </div>

            {/* History Drawer Toggle */}
            <button
              onClick={() => setShowHistory(true)}
              className="px-3 py-1.5 text-xs text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800 rounded-lg border border-slate-800 hover:border-slate-700 transition-colors flex items-center gap-1.5"
              title="Open Compilation History"
            >
              <History className="w-3.5 h-3.5 text-indigo-400" />
              <span className="hidden sm:inline">History</span>
              {history.length > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-indigo-500/20 text-indigo-300 font-mono text-[10px] border border-indigo-500/30">
                  {history.length}
                </span>
              )}
            </button>

            <button
              onClick={handleReset}
              className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors border border-transparent hover:border-slate-700"
              title="Reset Editor"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* History Slide-over Drawer */}
      {showHistory && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-xs">
          <div className="w-full max-w-md bg-[#0c1222] border-l border-slate-800 h-full p-5 flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-indigo-400" />
                <h3 className="font-semibold text-sm text-slate-200">Compilation History</h3>
                <span className="text-xs text-slate-500 font-mono">({history.length})</span>
              </div>
              <div className="flex items-center gap-2">
                {history.length > 0 && (
                  <button
                    onClick={clearHistory}
                    className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors"
                    title="Clear All History"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
                <button
                  onClick={() => setShowHistory(false)}
                  className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
              {history.length === 0 ? (
                <div className="h-40 flex flex-col items-center justify-center text-center text-xs text-slate-500">
                  <Clock className="w-6 h-6 mb-2 text-slate-600" />
                  <span>No prompts compiled yet in this session.</span>
                </div>
              ) : (
                history.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => loadFromHistory(item)}
                    className="p-3 rounded-xl bg-slate-900/60 hover:bg-indigo-950/40 border border-slate-800/80 hover:border-indigo-500/40 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-semibold text-slate-200 group-hover:text-indigo-300 truncate max-w-[200px]">
                        {item.domain}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-slate-500 font-mono">{item.timestamp}</span>
                        <span
                          className={`text-[10px] font-bold px-1.5 py-0.2 rounded font-mono ${
                            item.score >= 85
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}
                        >
                          {item.score}
                        </span>
                      </div>
                    </div>
                    <div className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                      {item.detail}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Panel: Configuration & Input */}
        <div className="lg:col-span-5 flex flex-col gap-5">
          {/* Preset Demonstrations Bar */}
          <div className="bg-[#0e1628] rounded-2xl p-4 border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-indigo-400" />
                Enterprise Scenarios
              </span>
              <span className="text-[11px] text-slate-500">One-click Presets</span>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {PRESET_SCENARIOS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => loadScenario(s)}
                  className="text-left p-2.5 rounded-xl bg-slate-900/60 hover:bg-indigo-950/40 border border-slate-800 hover:border-indigo-500/40 transition-all text-xs group cursor-pointer"
                >
                  <div className="font-semibold text-slate-200 group-hover:text-indigo-300 flex items-center justify-between">
                    <span>{s.title}</span>
                    <span className="text-[10px] text-slate-500 group-hover:text-indigo-400 font-mono">
                      {s.domain}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 truncate mt-0.5">{s.detail}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Core Input Form */}
          <div className="bg-[#0e1628] rounded-2xl p-5 border border-slate-800 shadow-xl flex flex-col gap-4">
            {/* Role / Persona Input */}
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
                  Target Role / Persona
                  <span className="text-[11px] font-normal text-slate-500">(Optional)</span>
                </label>
              </div>
              <input
                type="text"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                placeholder="e.g. Senior Cloud Architect, Doctor, Teacher..."
                className="w-full bg-[#090d16] border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
              <div className="flex flex-wrap gap-1.5 mt-1">
                {POPULAR_ROLES.map((r, i) => (
                  <button
                    key={i}
                    onClick={() => setRole(r)}
                    className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800/60 hover:bg-slate-700/80 text-slate-400 hover:text-slate-200 border border-slate-800 transition-colors cursor-pointer"
                  >
                    + {r}
                  </button>
                ))}
              </div>
            </div>

            {/* Task Detail / Prompt Intent Textarea */}
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
                  Task Detail & Core Intent
                  <span className="text-rose-400">*</span>
                </label>
                <span className="text-[11px] text-slate-500">{detail.length} chars</span>
              </div>
              <textarea
                rows={5}
                value={detail}
                onChange={(e) => {
                  setDetail(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="Describe what you want to build, plan, research, or solve. Supports one-word inputs, full technical briefs, or multiple languages (English, ગુજરાતી, हिन्दी, etc.)..."
                className="w-full bg-[#090d16] border border-slate-700 rounded-xl p-3.5 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all leading-relaxed resize-none"
              />
            </div>

            {/* Target LLM Optimizer Selector */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col gap-1.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                  <Bot className="w-3.5 h-3.5 text-cyan-400" />
                  Target Downstream LLM
                </span>
                <span className="text-[10px] text-slate-500 font-mono">Format Optimizer</span>
              </div>
              <select
                value={targetLLM}
                onChange={(e) => setTargetLLM(e.target.value)}
                className="w-full bg-[#090d16] border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-xs"
              >
                {TARGET_LLMS.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Collapsible Advanced Parameters */}
            <div className="border border-slate-800 rounded-xl bg-slate-900/40 overflow-hidden">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="w-full px-4 py-3 flex items-center justify-between text-xs font-medium text-slate-300 hover:text-white transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Calibrated Execution Parameters</span>
                </div>
                {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showAdvanced && (
                <div className="p-4 pt-2 border-t border-slate-800/60 flex flex-col gap-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Response Language</label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full bg-[#090d16] border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      {LANGUAGES.map((l) => (
                        <option key={l.value} value={l.value}>
                          {l.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Persona Tone</label>
                    <select
                      value={tone}
                      onChange={(e) => setTone(e.target.value)}
                      className="w-full bg-[#090d16] border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      {TONES.map((t) => (
                        <option key={t.value} value={t.value}>
                          {t.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Output Blueprint Format</label>
                    <select
                      value={format}
                      onChange={(e) => setFormat(e.target.value)}
                      className="w-full bg-[#090d16] border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      {OUTPUT_FORMATS.map((f) => (
                        <option key={f.value} value={f.value}>
                          {f.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}
            </div>

            {/* Error Banner */}
            {error && (
              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div className="leading-relaxed">{error}</div>
              </div>
            )}

            {/* Action Trigger Button */}
            <button
              onClick={handleGenerate}
              disabled={loading || !detail.trim()}
              className="w-full py-3.5 px-4 rounded-xl font-semibold text-sm bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white shadow-lg shadow-indigo-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 group cursor-pointer active:scale-[0.99]"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Reasoning & Compiling...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 text-cyan-200 group-hover:scale-110 transition-transform" />
                  <span>Execute Cognitive Compiler</span>
                  <span className="text-[11px] opacity-75 font-mono ml-1 font-normal">
                    (Ctrl + Enter)
                  </span>
                </>
              )}
            </button>
          </div>

          {/* AI Reasoning Pipeline Architecture Flow */}
          
        </div>

        {/* Right Panel: Output Workspace */}
        <div className="lg:col-span-7 flex flex-col gap-5">
          {!result && !loading && (
            <div className="h-full min-h-120 bg-[#0e1628]/40 border-2 border-dashed border-slate-800/80 rounded-2xl p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4 text-indigo-400">
                <FileText className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-semibold text-slate-200 mb-1">
                Awaiting Input Specification
              </h3>
              <p className="text-sm text-slate-400 max-w-md mb-6 leading-relaxed">
                Provide a role and task detail on the left, or select an enterprise scenario above to compile an authoritative Master Prompt.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-lg text-left">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-1.5 text-indigo-400 font-semibold text-xs mb-1">
                    <ShieldCheck className="w-3.5 h-3.5" /> Declarative Contracts
                  </div>
                  <p className="text-[11px] text-slate-400">9 schema-enforced blueprints with strict required headings.</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-1.5 text-cyan-400 font-semibold text-xs mb-1">
                    <Gauge className="w-3.5 h-3.5" /> Score Honesty Gate
                  </div>
                  <p className="text-[11px] text-slate-400">Hard check fails cap score at 60 and set draft status.</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-1.5 text-emerald-400 font-semibold text-xs mb-1">
                    <Layers className="w-3.5 h-3.5" /> Product Isolation
                  </div>
                  <p className="text-[11px] text-slate-400">Brand names never merge into technical subject graphs.</p>
                </div>
              </div>
            </div>
          )}

          {loading && (
            <div className="h-full min-h-120 bg-[#0e1628] border border-slate-800 rounded-2xl p-8 flex flex-col items-center justify-center text-center">
              <div className="w-14 h-14 rounded-2xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center mb-5 relative">
                <div className="absolute inset-0 rounded-2xl border-2 border-indigo-400 border-t-transparent animate-spin"></div>
                <Sparkles className="w-6 h-6 text-indigo-300" />
              </div>
              <h3 className="text-base font-semibold text-slate-100 mb-2">
                Running Cognitive Reasoning Pipeline
              </h3>
              <p className="text-xs font-mono text-cyan-400 animate-pulse">
                {loadingStage}
              </p>
            </div>
          )}

          {result && !loading && (
            <div className="bg-[#0e1628] rounded-2xl border border-slate-800 shadow-xl overflow-hidden flex flex-col">
              {/* Output Top Bar */}
              <div className="p-4 sm:p-5 border-b border-slate-800/80 bg-[#0b1120] flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  {/* Quality Score Badge */}
                  <div
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border ${
                      promptScoreNumber >= 85
                        ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                        : "bg-amber-500/10 border-amber-500/20 text-amber-400"
                    }`}
                  >
                    <Gauge className="w-4 h-4" />
                    <span className="font-bold text-sm">{promptScoreNumber}</span>
                    <span className="text-[11px] font-medium opacity-80">/ 100 Quality</span>
                  </div>

                  {/* Metadata Chips */}
                  {result.metadata && (
                    <div className="hidden sm:flex items-center gap-1.5 flex-wrap">
                      <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-[11px] text-slate-300 border border-slate-700/60 font-medium">
                        {result.metadata.detected_domain}
                      </span>
                      <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-[11px] text-indigo-300 border border-slate-700/60 font-medium uppercase font-mono">
                        {result.metadata.detected_intent}
                      </span>
                      {result.metadata.aligned_role && (
                        <span className="px-2.5 py-1 rounded-lg bg-cyan-950/60 text-[11px] text-cyan-300 border border-cyan-800/60 font-medium">
                          Role: {result.metadata.aligned_role}
                        </span>
                      )}
                      <span className="px-2 py-1 rounded-lg bg-slate-900 text-[11px] text-slate-400 font-mono">
                        {result.metadata.processing_time_ms} ms
                      </span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopy}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleDownload}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer"
                    title="Download as Markdown"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download</span>
                  </button>

                  {/* Feedback Loop Buttons */}
                  <div className="flex items-center gap-1 border-l border-slate-700/80 pl-2 ml-1">
                    <button
                      onClick={() => handleFeedback("up")}
                      disabled={feedbackSubmitting}
                      className={`px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-all flex items-center gap-1 cursor-pointer ${
                        feedbackRating === "up"
                          ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                          : "bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700"
                      }`}
                      title="Mark prompt as helpful (stores golden exemplar to learning memory)"
                    >
                      <ThumbsUp className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="hidden sm:inline">Helpful</span>
                    </button>

                    <button
                      onClick={() => handleFeedback("down")}
                      disabled={feedbackSubmitting}
                      className={`px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-all flex items-center gap-1 cursor-pointer ${
                        feedbackRating === "down"
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                          : "bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700"
                      }`}
                      title="Mark prompt as needing improvement (records corrective memory)"
                    >
                      <ThumbsDown className="w-3.5 h-3.5 text-rose-400" />
                      <span className="hidden sm:inline">Refine</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Token & Context Telemetry Live Bar */}
              {tokenTelemetry && (
                <div className="px-4 py-2 bg-[#090e1a] border-b border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono flex-wrap gap-2">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1 text-slate-300">
                      <Binary className="w-3.5 h-3.5 text-indigo-400" />
                      <strong className="text-indigo-300">{tokenTelemetry.estTokens.toLocaleString()}</strong> est. tokens
                    </span>
                    <span>&bull;</span>
                    <span>{tokenTelemetry.charCount.toLocaleString()} chars</span>
                    <span>&bull;</span>
                    <span>{tokenTelemetry.words.toLocaleString()} words</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-slate-400">
                      ~{tokenTelemetry.estReadingTimeMin} min read
                    </span>
                    <span>&bull;</span>
                    <span className="text-cyan-400">
                      {tokenTelemetry.contextFootprintPercent}% of 128k context
                    </span>
                  </div>
                </div>
              )}

              {/* Feedback Success Notification */}
              {feedbackToast && (
                <div className="mx-4 mt-3 px-3.5 py-2 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{feedbackToast}</span>
                </div>
              )}

              {/* Smart Clarification Prompts (Interactive Disambiguation) */}
              {result.clarifications && result.clarifications.length > 0 && (
                <div className="mx-4 my-3 p-3.5 rounded-xl bg-indigo-950/30 border border-indigo-500/30 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Lightbulb className="w-4 h-4 text-amber-400 shrink-0" />
                      <span className="text-xs font-semibold text-indigo-200">
                        Smart Disambiguation & Clarification Suggestions
                      </span>
                    </div>
                    <span className="text-[10px] text-indigo-400/80 font-mono">
                      Click any pill to append to input
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    The compiler noticed your input is terse or broad. Click any suggestion below to refine parameters:
                  </p>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {result.clarifications.map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleApplyClarification(q)}
                        className="text-left text-xs bg-slate-900/80 hover:bg-indigo-900/50 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-indigo-500/20 hover:border-indigo-400/50 transition-colors flex items-center gap-1.5 cursor-pointer group"
                        title="Append to prompt input"
                      >
                        <MessageSquarePlus className="w-3.5 h-3.5 text-indigo-400 group-hover:text-indigo-300 shrink-0" />
                        <span>{q}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Navigation Tabs */}
              <div className="flex border-b border-slate-800 px-4 bg-[#090d16] overflow-x-auto">
                <button
                  onClick={() => setActiveTab("prompt")}
                  className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer ${
                    activeTab === "prompt"
                      ? "border-indigo-500 text-indigo-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Master Prompt</span>
                </button>
                <button
                  onClick={() => setActiveTab("diff")}
                  className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer ${
                    activeTab === "diff"
                      ? "border-indigo-500 text-indigo-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Columns className="w-3.5 h-3.5" />
                  <span>Input vs Master Diff</span>
                </button>
                <button
                  onClick={() => setActiveTab("cognitive")}
                  className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer ${
                    activeTab === "cognitive"
                      ? "border-indigo-500 text-indigo-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Cognitive Reasoning & Schema</span>
                </button>
                <button
                  onClick={() => setActiveTab("assumptions")}
                  className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer ${
                    activeTab === "assumptions"
                      ? "border-indigo-500 text-indigo-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <BookOpen className="w-3.5 h-3.5" />
                  <span>Documented Assumptions ({result.assumptions.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab("quality")}
                  className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer ${
                    activeTab === "quality"
                      ? "border-indigo-500 text-indigo-400"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Gauge className="w-3.5 h-3.5" />
                  <span>Quality Rubric Breakdown</span>
                </button>
              </div>

              {/* Tab Contents */}
              <div className="p-5 overflow-y-auto max-h-150">
                {activeTab === "prompt" && (
                  <div className="space-y-4">
                    <pre className="whitespace-pre-wrap font-mono text-xs sm:text-sm text-slate-200 leading-relaxed bg-[#070b14] p-4 rounded-xl border border-slate-800/80 select-all selection:bg-indigo-600 selection:text-white">
                      {displayedPrompt}
                    </pre>
                  </div>
                )}

                {activeTab === "diff" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-400 pb-1 border-b border-slate-800">
                        <span>Raw User Input</span>
                        <span className="text-[10px] text-slate-500 font-mono">{detail.length} chars</span>
                      </div>
                      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 font-mono whitespace-pre-wrap leading-relaxed h-full">
                        {role && (
                          <div className="text-indigo-400 mb-2 font-bold">
                            Role: {role}
                          </div>
                        )}
                        <div>{detail}</div>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <div className="flex items-center justify-between text-xs font-semibold text-indigo-400 pb-1 border-b border-slate-800">
                        <span>Compiled Master Prompt ({targetLLM})</span>
                        <span className="text-[10px] text-indigo-300 font-mono">{displayedPrompt.length} chars</span>
                      </div>
                      <pre className="p-4 rounded-xl bg-[#070b14] border border-indigo-500/20 text-xs text-slate-200 font-mono whitespace-pre-wrap leading-relaxed overflow-y-auto max-h-120">
                        {displayedPrompt}
                      </pre>
                    </div>
                  </div>
                )}

                {activeTab === "cognitive" && (
                  <div className="space-y-5">
                    {/* Persona & Alignment Card */}
                    <div className="p-4 rounded-xl bg-[#070b14] border border-slate-800 space-y-3">
                      <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4" />
                        Role Intelligence & Task Alignment
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                          <span className="text-slate-400 block text-[11px]">Requested Role</span>
                          <span className="text-slate-200 font-semibold">
                            {result.metadata?.original_role || "None (Autonomous Synthesis)"}
                          </span>
                        </div>
                        <div className="p-3 rounded-lg bg-indigo-950/40 border border-indigo-500/30">
                          <span className="text-indigo-300 block text-[11px]">Final Aligned Persona</span>
                          <span className="text-emerald-300 font-bold">
                            {result.metadata?.aligned_role || "Domain Specialist"}
                          </span>
                        </div>
                      </div>
                      {result.metadata?.cognitive_reasoning?.role_adjustment_rationale && (
                        <p className="text-xs text-slate-400 italic bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/60">
                          &ldquo;{result.metadata.cognitive_reasoning.role_adjustment_rationale}&rdquo;
                        </p>
                      )}
                    </div>

                    {/* Linguistic & Psychological Affect Profile */}
                    {(result.metadata?.writing_style || result.metadata?.user_emotion || result.metadata?.formality_level) && (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                          <span className="text-slate-400 block text-[11px] mb-1">Writing Style</span>
                          <span className="text-cyan-300 font-semibold">
                            {result.metadata?.writing_style || "Technical"}
                          </span>
                        </div>
                        <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                          <span className="text-slate-400 block text-[11px] mb-1">Formality Register</span>
                          <span className="text-indigo-300 font-semibold">
                            {result.metadata?.formality_level || "Professional-Neutral"}
                          </span>
                        </div>
                        <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                          <span className="text-slate-400 block text-[11px] mb-1">User Emotion</span>
                          <span className="text-emerald-300 font-semibold">
                            {result.metadata?.user_emotion || "Analytical"}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Audience & Proficiency Profile */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                      <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                        <span className="text-slate-400 block text-[11px] mb-1">Target Audience</span>
                        <span className="text-slate-200 font-semibold">
                          {result.metadata?.target_audience || "General Stakeholders"}
                        </span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                        <span className="text-slate-400 block text-[11px] mb-1">Proficiency Level</span>
                        <span className="text-cyan-300 font-semibold">
                          {result.metadata?.experience_level || "Intermediate"}
                        </span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                        <span className="text-slate-400 block text-[11px] mb-1">Risk Assessment</span>
                        <span className="text-amber-400 font-semibold">
                          {result.metadata?.risk_level || "Low"} Risk
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === "assumptions" && (
                  <div className="space-y-3">
                    <p className="text-xs text-slate-400 leading-relaxed">
                      The autonomous cognitive pipeline formulated the following smart assumptions to fill unspecified gaps without blocking execution:
                    </p>
                    <div className="grid grid-cols-1 gap-2.5">
                      {result.assumptions.map((asm, idx) => (
                        <div
                          key={idx}
                          className="p-3 rounded-xl bg-[#070b14] border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5"
                        >
                          <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                          <span className="leading-relaxed">{asm}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === "quality" && (
                  <div className="space-y-5">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {result.breakdown && (
                        <>
                          <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-slate-300 font-medium">Clarity</span>
                              <span className="text-indigo-400 font-mono font-bold">
                                {result.breakdown.clarity} / 20
                              </span>
                            </div>
                            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                              <div
                                className="bg-indigo-500 h-full rounded-full"
                                style={{ width: `${(result.breakdown.clarity / 20) * 100}%` }}
                              ></div>
                            </div>
                          </div>

                          <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-slate-300 font-medium">Specificity</span>
                              <span className="text-indigo-400 font-mono font-bold">
                                {result.breakdown.specificity} / 20
                              </span>
                            </div>
                            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                              <div
                                className="bg-indigo-500 h-full rounded-full"
                                style={{ width: `${(result.breakdown.specificity / 20) * 100}%` }}
                              ></div>
                            </div>
                          </div>

                          <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-slate-300 font-medium">Context</span>
                              <span className="text-cyan-400 font-mono font-bold">
                                {result.breakdown.context} / 15
                              </span>
                            </div>
                            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                              <div
                                className="bg-cyan-500 h-full rounded-full"
                                style={{ width: `${(result.breakdown.context / 15) * 100}%` }}
                              ></div>
                            </div>
                          </div>

                          <div className="p-3.5 rounded-xl bg-[#070b14] border border-slate-800">
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-slate-300 font-medium">Operational Constraints</span>
                              <span className="text-cyan-400 font-mono font-bold">
                                {result.breakdown.constraints} / 15
                              </span>
                            </div>
                            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                              <div
                                className="bg-cyan-500 h-full rounded-full"
                                style={{ width: `${(result.breakdown.constraints / 15) * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        </>
                      )}
                    </div>

                    {/* Honest Scoring Breakdown & Invariant Penalties */}
                    <div className="p-4 rounded-xl bg-[#070b14] border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                          <ShieldCheck className="w-4 h-4 text-cyan-400" />
                          Invariant Enforcement & Audit Telemetry (S7)
                        </span>
                        <span className="text-[11px] font-mono text-slate-400">
                          Cap Rule: score &le; 60 on hard fail
                        </span>
                      </div>

                      {result.metadata?.penalties && result.metadata.penalties.length > 0 ? (
                        <div className="space-y-2">
                          <span className="text-[11px] text-rose-400 font-semibold block">Penalties Applied:</span>
                          <ul className="space-y-1.5 text-xs">
                            {result.metadata.penalties.map((p, idx) => (
                              <li key={idx} className="flex items-start justify-between gap-2 p-2.5 rounded-lg bg-rose-950/25 border border-rose-900/40 text-rose-200">
                                <div>
                                  <span className="font-mono font-bold text-rose-400 mr-2 shrink-0">[-{p.penalty}] {p.name || p.code}:</span>
                                  <span>{p.reason}</span>
                                </div>
                                {p.is_hard_check && (
                                  <span className="shrink-0 px-2 py-0.5 rounded bg-rose-900/60 border border-rose-700/60 text-[10px] uppercase font-bold text-rose-200">
                                    Hard Check (Capped at 60)
                                  </span>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ) : (
                        <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/40 text-emerald-400 text-xs flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                          <span>Zero Invariant Penalties Applied. All S7 checks verified. Honest score: {promptScoreNumber}/100</span>
                        </div>
                      )}
                    </div>

                    {result.improvements && result.improvements.length > 0 && (
                      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                        <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          Auto-Improvement Insights
                        </span>
                        <ul className="space-y-1.5 text-xs text-slate-400">
                          {result.improvements.map((imp, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-indigo-400 font-mono font-bold">&bull;</span>
                              <span>{imp}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
