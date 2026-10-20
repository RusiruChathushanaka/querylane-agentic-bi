"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { workspacePath } from "@/lib/workspace-links";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  FileChartColumn,
  ArrowDown,
  ArrowRight,
  ArrowUp,
  AudioLines,
  BarChart3,
  BookOpen,
  Check,
  ChevronRight,
  CircleHelp,
  Command,
  Database,
  GitFork,
  Globe2,
  Layers3,
  Link2,
  LoaderCircle,
  Menu,
  MessageSquare,
  Mic,
  MicOff,
  Plus,
  Radio,
  Search,
  Settings2,
  PanelsTopLeft,
  ShieldCheck,
  Square,
  Target,
  TrendingUp,
  Users,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { MessageContent } from "@/components/markdown-content";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupTextarea,
} from "@/components/ui/input-group";
import { Field, FieldLabel } from "@/components/ui/field";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from "@/components/ui/empty";
import { api, streamRun } from "@/lib/api";
import { LiveVoice } from "@/lib/voice";
import type {
  Artifact,
  Connection,
  Conversation,
  Message,
  StreamEvent,
} from "@/lib/types";
import { cn } from "@/lib/utils";
import { usePreferences } from "@/hooks/use-preferences";
import { useAppMotion } from "@/hooks/use-app-motion";
import { Reveal } from "@/components/motion/reveal";
import { AnalysisProgress } from "@/components/motion/analysis-progress";
import { SkillAttachments } from "@/components/skill-attachments";
import { ConversationReports } from "@/components/report-run-card";
import type { ReportRun } from "@/lib/report-types";
import { SkillEvidence } from "@/components/skill-evidence";
import { SPRING_PRESS, EASE_OUT } from "@/lib/ease";

const ResultCard = dynamic(() => import("./result-card"), {
  loading: () => <Skeleton className="result-loading" />,
});
const suggestions = [
  {
    icon: TrendingUp,
    title: "See the bigger picture",
    question:
      "Show monthly merchandise revenue across all complete months of available history as a line chart in USD. Use completed orders, after discounts and before refunds, tax and shipping. State the observation cutoff.",
    detail: "Explore monthly merchandise revenue over time",
    source: "BigQuery",
    sourceId: "bigquery",
  },
  {
    icon: Target,
    title: "Actuals meet ambition",
    question:
      "Compare regional merchandise revenue with regional revenue targets across the complete months covered by both sources. Show actual revenue and target revenue in USD for each region. Actual revenue uses completed orders, after discounts and before refunds, tax and shipping.",
    detail: "Compare regional revenue and full-month targets",
    source: "Cross-source",
    sourceId: "all",
  },
  {
    icon: Users,
    title: "Know your customers",
    question:
      "Use an ad hoc breakdown of merchandise revenue by customer segment across all available completed-order history. Revenue is after discounts and before refunds, tax and shipping. Connect sales to customer profiles by customer_id and show a bar chart in USD. This breakdown is not a published catalog definition.",
    detail: "Explore sales by segment with an ad hoc breakdown",
    source: "Cross-source",
    sourceId: "all",
  },
  {
    icon: BarChart3,
    title: "Find what sells",
    question:
      "Break down merchandise revenue by product category across all available completed-order history as a bar chart in USD. Revenue is after discounts and before refunds, tax and shipping. Use line revenue for the category breakdown so order totals are not duplicated.",
    detail: "Compare product categories by merchandise revenue",
    source: "BigQuery",
    sourceId: "bigquery",
  },
];

function Mark({ small = false }: { small?: boolean }) {
  return (
    <span
      className={cn("brand-mark", small && "brand-mark-small")}
      aria-hidden="true"
    >
      <svg viewBox="0 0 32 32" fill="none">
        <path
          d="M8 7v7a5 5 0 0 0 5 5h11M8 25v-6a5 5 0 0 1 5-5h11"
          stroke="currentColor"
          strokeWidth="2.6"
          strokeLinecap="round"
        />
        <circle cx="8" cy="7" r="2.5" fill="currentColor" />
        <circle cx="8" cy="25" r="2.5" fill="currentColor" />
        <path
          d="m21 11 4 3-4 3m0-1 4 3-4 3"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}

export default function Workspace() {
  const router = useRouter();
  const { preferences } = usePreferences();
  const { reduced, hydrated } = useAppMotion();
  const [connections, setConnections] = useState<Connection[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Record<string, Artifact>>({});
  const [question, setQuestion] = useState("");
  const [advanced, setAdvanced] = useState(false);
  const [reportStyle, setReportStyle] = useState<"business" | "technical">(
    "business",
  );
  const [reportsEnabled, setReportsEnabled] = useState(false);
  const [reportRefresh, setReportRefresh] = useState(0);
  const reportRequest = useRef<{ signature: string; key: string } | null>(null);
  useEffect(() => {
    let cancelled = false;
    void api<{ enabled: boolean }>("/reports/config")
      .then((v) => {
        if (!cancelled) setReportsEnabled(v.enabled);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);
  const [sourceOverride, setSource] = useState<string | null>(null);
  const source = sourceOverride ?? preferences.defaultSource;
  const [runId, setRunId] = useState<string | null>(null);
  const [progress, setProgress] = useState("");
  const [stage, setStage] = useState("");
  const [draftArtifact, setDraftArtifact] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [forking, setForking] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [updatingSkills, setUpdatingSkills] = useState(false);
  const [mode, setMode] = useState("");
  const [dataPeriod, setDataPeriod] = useState("SYNTHETIC RETAIL");
  const [voiceState, setVoiceState] = useState("off");
  const [voiceText, setVoiceText] = useState("");
  const [level, setLevel] = useState(0);
  const [muted, setMuted] = useState(false);
  const [search, setSearch] = useState("");
  const [schemaSource, setSchemaSource] = useState<string | null>(null);
  const [schemaLoading, setSchemaLoading] = useState(false);
  const schemaRequest = useRef(0);
  const [schema, setSchema] = useState<
    {
      table: string;
      description: string;
      columns: { name: string; type: string }[];
    }[]
  >([]);
  const [schemaError, setSchemaError] = useState("");
  const controller = useRef<AbortController | null>(null);
  const artifactCache = useRef<Record<string, Artifact>>({});
  const voice = useRef<LiveVoice | null>(null);
  const bottom = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  const activeConversation = useRef<string | null>(null);
  const analysisToast = useRef<string | null>(null);
  const followLatest = useRef(true);
  const contentResize = useRef<ResizeObserver | null>(null);
  const registerBottom = useCallback(
    (node: HTMLDivElement | null) => {
      contentResize.current?.disconnect();
      bottom.current = node;
      if (node && preferences.autoScroll && followLatest.current)
        node.scrollIntoView({ behavior: "instant", block: "end" });
      if (node?.parentElement && preferences.autoScroll) {
        const observer = new ResizeObserver(() => {
          if (followLatest.current && node.isConnected)
            node.scrollIntoView({ behavior: "instant", block: "end" });
        });
        observer.observe(node.parentElement);
        contentResize.current = observer;
      }
    },
    [preferences.autoScroll],
  );

  const refreshList = useCallback(async () => {
    const result = await api<{ conversations: Conversation[] }>(
      "/conversations",
    );
    setConversations(result.conversations);
  }, []);

  const loadArtifact = useCallback(async (id: string) => {
    if (artifactCache.current[id]) return;
    const artifact = await api<Artifact>(`/artifacts/${id}`);
    artifactCache.current[id] = artifact;
    setArtifacts((previous) => ({ ...previous, [id]: artifact }));
  }, []);

  const loadMessages = useCallback(
    async (id: string) => {
      const result = await api<{
        conversation: Conversation;
        messages: Message[];
      }>(`/conversations/${id}`);
      if (activeConversation.current !== id) return result;
      setConversation(result.conversation);
      setMessages(result.messages);
      await Promise.all(
        result.messages
          .filter((message) => message.artifact_id)
          .map((message) => loadArtifact(message.artifact_id!)),
      );
      return result;
    },
    [loadArtifact],
  );

  const followRun = useCallback(
    async (id: string, chatId: string) => {
      controller.current?.abort();
      const streamController = new AbortController();
      controller.current = streamController;
      setRunId(id);
      const feedbackId = `analysis:${id}`;
      analysisToast.current = feedbackId;
      let terminal = false;
      toast.loading("Analyzing your question", {
        id: feedbackId,
        description: "Inspecting sources and preparing a read-only query.",
      });
      try {
        await streamRun(id, streamController.signal, (event: StreamEvent) => {
          if (activeConversation.current !== chatId) return;
          if (event.type === "progress") {
            setProgress(String(event.data.message));
            setStage(String(event.data.stage ?? "schema"));
          }
          if (event.type === "artifact") {
            const artifactId = String(event.data.id);
            void loadArtifact(artifactId)
              .then(() => {
                if (activeConversation.current === chatId)
                  setDraftArtifact(artifactId);
              })
              .catch((error) => setError(error.message));
          }
          if (event.type === "answer") {
            setProgress("Answer ready");
          }
          if (event.type === "complete") {
            terminal = true;
            toast.success("Answer ready", {
              id: feedbackId,
              description: "Results and query evidence are ready to explore.",
              duration: 4500,
            });
          }
          if (event.type === "error") {
            terminal = true;
            const detail = String(event.data.message);
            if (event.data.code === "cancelled") {
              toast.info("Analysis stopped", {
                id: feedbackId,
                description: "The run has confirmed cancellation.",
                duration: 4500,
              });
            } else {
              setError(detail);
              toast.error("Analysis could not finish", {
                id: feedbackId,
                description: detail,
                duration: 6000,
              });
            }
          }
        });
        if (
          !streamController.signal.aborted &&
          activeConversation.current === chatId
        ) {
          await loadMessages(chatId);
          setDraftArtifact(null);
          await refreshList();
        }
      } catch (error) {
        if (!streamController.signal.aborted) {
          terminal = true;
          toast.error("Analysis connection interrupted", {
            id: feedbackId,
            description:
              "Reopen the conversation to reconnect to the saved run.",
            duration: 6000,
          });
          setError(
            error instanceof Error
              ? error.message
              : "The analysis connection failed.",
          );
        }
      } finally {
        if (controller.current === streamController) {
          if (!terminal) toast.dismiss(feedbackId);
          analysisToast.current = null;
          setStopping(false);
        }
        if (
          !streamController.signal.aborted &&
          activeConversation.current === chatId
        ) {
          setRunId(null);
          setProgress("");
          setStage("");
        }
      }
    },
    [loadArtifact, loadMessages, refreshList],
  );

  const selectConversation = useCallback(
    async (id: string) => {
      setAdvanced(false);
      followLatest.current = true;
      controller.current?.abort();
      if (analysisToast.current) toast.dismiss(analysisToast.current);
      voice.current?.stop();
      setVoiceState("off");
      setRunId(null);
      setDraftArtifact(null);
      setError("");
      setMessages([]);
      activeConversation.current = id;
      history.replaceState(null, "", workspacePath(id, window.location.search));
      try {
        const result = await loadMessages(id);
        if (activeConversation.current === id) {
          setSource(result.conversation.source);
          if (
            result.conversation.active_run &&
            result.conversation.lease_until * 1000 > Date.now()
          )
            void followRun(result.conversation.active_run, id);
        }
      } catch (error) {
        setError(
          error instanceof Error
            ? error.message
            : "Could not load this conversation.",
        );
        toast.error("Conversation could not open", {
          id: "conversation-load",
          description: "Try opening it again from the public history.",
        });
      }
    },
    [followRun, loadMessages, setSource, setVoiceState],
  );

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      api<{ mode: string; period?: string; connections: Connection[] }>(
        "/connections",
      ),
      api<{ conversations: Conversation[] }>("/conversations"),
    ])
      .then(([sources, chats]) => {
        if (cancelled) return;
        setConnections(sources.connections);
        setMode(sources.mode);
        setDataPeriod(sources.period ?? "SYNTHETIC RETAIL");
        setConversations(chats.conversations);
        setLoading(false);
        const chatId = new URLSearchParams(window.location.search).get("chat");
        if (chatId && /^[a-f0-9]{32}$/.test(chatId))
          void selectConversation(chatId);
      })
      .catch((error) => {
        if (!cancelled) {
          setError(error.message);
          toast.error("Workspace could not connect", {
            id: "workspace-load",
            description: error.message,
            action: { label: "Retry", onClick: () => window.location.reload() },
          });
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
      controller.current?.abort();
      if (analysisToast.current) toast.dismiss(analysisToast.current);
      toast.dismiss("voice-session");
      voice.current?.stop();
    };
  }, [selectConversation]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (document.visibilityState !== "visible") return;
      void refreshList().catch(() => {});
      if (activeConversation.current && !runId && voiceState === "off")
        void loadMessages(activeConversation.current).catch(() => {});
    }, 8000);
    return () => clearInterval(interval);
  }, [runId, voiceState, loadMessages, refreshList]);

  useEffect(() => {
    if (
      preferences.autoScroll &&
      followLatest.current &&
      (messages.length || progress || draftArtifact)
    )
      bottom.current?.scrollIntoView({ behavior: "instant", block: "end" });
  }, [messages.length, progress, draftArtifact, preferences.autoScroll]);

  function newConversation() {
    setAdvanced(false);
    followLatest.current = true;
    controller.current?.abort();
    if (analysisToast.current) toast.dismiss(analysisToast.current);
    toast.dismiss("voice-session");
    voice.current?.stop();
    activeConversation.current = null;
    setConversation(null);
    setSource(null);
    setMessages([]);
    setQuestion("");
    setError("");
    setRunId(null);
    setProgress("");
    setDraftArtifact(null);
    setVoiceState("off");
    history.replaceState(null, "", workspacePath());
    input.current?.focus();
  }

  async function ensureConversation(requestedSource?: string) {
    if (
      conversation &&
      activeConversation.current === conversation.id &&
      (!requestedSource || conversation.source === requestedSource)
    )
      return conversation;
    const questionSource = requestedSource ?? source;
    const created = await api<Conversation>("/conversations", {
      method: "POST",
      body: JSON.stringify({ source: questionSource }),
    });
    activeConversation.current = created.id;
    setConversation(created);
    setSource(questionSource);
    history.replaceState(null, "", workspacePath(created.id));
    await refreshList();
    return created;
  }

  function draftChartQuestion(text: string) {
    if (question.trim()) {
      toast.info("Your existing draft is still in the composer", {
        description:
          "Copy this chart question or clear your draft before trying again.",
        action: {
          label: "Copy chart question",
          onClick: () => {
            void navigator.clipboard
              .writeText(text)
              .then(() => toast.success("Chart question copied"))
              .catch(() => toast.error("Clipboard is unavailable."));
          },
        },
        duration: 8000,
      });
      return;
    }
    setQuestion(text.slice(0, 4000));
    window.requestAnimationFrame(() =>
      document.getElementById("question")?.focus(),
    );
    toast.info("Follow-up drafted", {
      description: "Review the question, then send when ready.",
    });
  }

  async function ask(text = question, requestedSource?: string) {
    if (
      !text.trim() ||
      updatingSkills ||
      starting ||
      runId ||
      voiceState === "live" ||
      voiceState === "connecting"
    )
      return;
    setStarting(true);
    followLatest.current = true;
    setError("");
    setQuestion("");
    setDraftArtifact(null);
    try {
      const chat = await ensureConversation(requestedSource);
      if (advanced) {
        const signature = JSON.stringify([
          chat.id,
          text.trim(),
          reportStyle,
          preferences.textModel,
        ]);
        if (reportRequest.current?.signature !== signature)
          reportRequest.current = { signature, key: crypto.randomUUID() };
        await api<ReportRun>(`/conversations/${chat.id}/reports`, {
          method: "POST",
          body: JSON.stringify({
            question: text.trim(),
            style: reportStyle,
            model:
              preferences.textModel === "default"
                ? undefined
                : preferences.textModel,
            idempotency_key: reportRequest.current.key,
          }),
        });
        reportRequest.current = null;
        setReportRefresh((v) => v + 1);
        toast.success("Advanced report requested", {
          description: "You can continue chatting while it works.",
          action: {
            label: "Reports",
            onClick: () => {
              router.push("/reports");
            },
          },
        });
        setAdvanced(false);
        return;
      }
      const response = await api<{ run_id: string }>(
        `/conversations/${chat.id}/turns`,
        {
          method: "POST",
          body: JSON.stringify({
            question: text.trim(),
            idempotency_key: crypto.randomUUID(),
            model:
              preferences.textModel === "default"
                ? undefined
                : preferences.textModel,
          }),
        },
      );
      await loadMessages(chat.id);
      setProgress("Inspecting sources and business context");
      void followRun(response.run_id, chat.id);
    } catch (error) {
      setQuestion(text);
      toast.error("Analysis could not start", {
        id: "analysis-start",
        description:
          error instanceof Error
            ? error.message
            : "Your question is still in the composer. Try again.",
      });
      setError(
        error instanceof Error
          ? error.message
          : "Could not start the analysis.",
      );
    } finally {
      setStarting(false);
    }
  }

  async function fork() {
    if (!conversation || forking) return;
    setForking(true);
    toast.loading("Forking this exploration", { id: "fork-conversation" });
    try {
      const created = await api<Conversation>(
        `/conversations/${conversation.id}/fork`,
        { method: "POST" },
      );
      await selectConversation(created.id);
      await refreshList();
      toast.success("Conversation forked", {
        id: "fork-conversation",
        description:
          "Your new exploration includes the original context and results.",
        duration: 4500,
      });
    } catch (error) {
      toast.error(
        error instanceof Error
          ? error.message
          : "Could not fork this conversation.",
        { id: "fork-conversation" },
      );
    } finally {
      setForking(false);
    }
  }

  async function cancelAnalysis() {
    if (!runId || stopping) return;
    setStopping(true);
    toast.loading("Stopping analysis…", {
      id: `analysis:${runId}`,
      description: "Waiting for the run to confirm cancellation.",
    });
    try {
      await api(`/runs/${runId}/cancel`, { method: "POST" });
    } catch (error) {
      setStopping(false);
      toast.error("Could not request a stop", {
        id: `analysis:${runId}`,
        description: error instanceof Error ? error.message : "Try again.",
      });
    }
  }

  async function startVoice() {
    if (runId || starting || updatingSkills) return;
    setVoiceState("connecting");
    setError("");
    setVoiceText("");
    toast.loading("Connecting to live voice", {
      id: "voice-session",
      description: "Allow microphone access when your browser asks.",
    });
    try {
      const chat = await ensureConversation();
      let transcriptRole: unknown;
      const session = new LiveVoice(
        (event) => {
          if (event.type === "ready") {
            setVoiceState("live");
            toast.success("Voice connected", {
              id: "voice-session",
              description: preferences.startMuted
                ? "Your microphone is muted. Unmute when you’re ready."
                : "You can speak now. Transcripts are visible in this public chat.",
              duration: 5000,
            });
          }
          if (event.type === "transcript") {
            const replace = event.replace || transcriptRole !== event.role;
            transcriptRole = event.role;
            setVoiceText((previous) =>
              ((replace ? "" : previous) + String(event.text)).slice(-1000),
            );
          }
          if (event.type === "tool_error") {
            toast.error("Voice analysis could not finish", {
              description: String(event.message),
            });
          }
          if (event.type === "artifact") {
            const data = event.data as { id: string };
            void loadArtifact(data.id);
            setDraftArtifact(data.id);
          }
          if (event.type === "turn_complete") {
            transcriptRole = undefined;
            void loadMessages(chat.id).then(() => setDraftArtifact(null));
            void refreshList();
          }
          if (
            ["error", "session_limit", "disconnected", "reconnect"].includes(
              event.type,
            )
          ) {
            setVoiceState("disconnected");
            setError(String(event.message));
            toast.error("Voice connection paused", {
              id: "voice-session",
              description: String(event.message),
              duration: 6000,
            });
            session.stop();
            void loadMessages(chat.id);
          }
          if (event.type === "stopped")
            setVoiceState((current) =>
              current === "disconnected" ? current : "off",
            );
        },
        setLevel,
        {
          spokenResponses: preferences.spokenResponses,
          startMuted: preferences.startMuted,
          analysisModel:
            preferences.textModel === "default"
              ? undefined
              : preferences.textModel,
        },
      );
      setMuted(preferences.startMuted);
      voice.current = session;
      await session.start(chat.id);
    } catch (error) {
      voice.current?.stop();
      setVoiceState("off");
      setError(
        error instanceof Error ? error.message : "Microphone could not start.",
      );
      toast.error("Voice could not start", {
        id: "voice-session",
        description:
          error instanceof Error
            ? error.message
            : "Check microphone permissions and try again.",
        duration: 6000,
      });
    }
  }

  async function openSchema(id: string) {
    const request = ++schemaRequest.current;
    setSchemaLoading(true);
    setSchemaSource(id);
    setSchema([]);
    setSchemaError("");
    try {
      const result = await api<{ tables: typeof schema }>(
        `/connections/${id}/schema`,
      );
      if (request !== schemaRequest.current) return;
      setSchema(result.tables);
    } catch (error) {
      if (request !== schemaRequest.current) return;
      setSchemaError(
        error instanceof Error ? error.message : "Schema unavailable.",
      );
      toast.error("Schema could not load", {
        id: `schema:${id}`,
        description:
          error instanceof Error
            ? error.message
            : "Try opening the source again.",
      });
    } finally {
      if (request === schemaRequest.current) setSchemaLoading(false);
    }
  }

  const busy = Boolean(
    updatingSkills ||
    runId ||
    starting ||
    voiceState === "live" ||
    voiceState === "connecting",
  );
  const sidebar = (
    <>
      <Link className="brand" href="/" aria-label="Querylane home">
        <Mark />
        <span>
          Querylane
          <span className="brand-subtitle">Agentic business intelligence</span>
        </span>
        <Badge variant="outline">DEMO</Badge>
      </Link>
      <Button className="new-chat" variant="outline" onClick={newConversation}>
        <Plus data-icon="inline-start" />
        New exploration<kbd>↗</kbd>
      </Button>
      <div className="sidebar-label history-label">
        PUBLIC EXPLORATIONS<span>{conversations.length}</span>
      </div>
      <div className="history-search">
        <Search aria-hidden />
        <input
          aria-label="Search public conversations"
          placeholder="Find a conversation"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>
      <nav className="conversation-list" aria-label="Public conversations">
        {conversations
          .filter((chat) =>
            chat.title.toLowerCase().includes(search.toLowerCase()),
          )
          .map((chat) => (
            <Button
              variant={conversation?.id === chat.id ? "secondary" : "ghost"}
              key={chat.id}
              onClick={() => void selectConversation(chat.id)}
            >
              <MessageSquare data-icon="inline-start" />
              <span className="truncate">{chat.title}</span>
              {chat.active_run && <span className="connection-dot" />}
            </Button>
          ))}
        {!loading && !conversations.length && (
          <p>Your first question starts a new exploration.</p>
        )}
      </nav>
      <div className="sidebar-footer">
        <Separator />
        <Button asChild variant="ghost" className="workspace-settings-link">
          <Link href="/dashboards">
            <PanelsTopLeft data-icon="inline-start" /> Dashboards
          </Link>
        </Button>
        <Button asChild variant="ghost" className="workspace-settings-link">
          <Link href="/reports">
            <FileChartColumn data-icon="inline-start" /> Reports
          </Link>
        </Button>
        <Button asChild variant="ghost" className="workspace-settings-link">
          <Link href="/metrics">
            <Target aria-hidden="true" data-icon="inline-start" /> Business metrics
          </Link>
        </Button>
        <Button asChild variant="ghost" className="workspace-settings-link">
          <Link href="/forecast-plans">
            <TrendingUp aria-hidden="true" data-icon="inline-start" /> Forecast plans
          </Link>
        </Button>
        <Button asChild variant="ghost" className="workspace-settings-link">
          <Link href="/skills">
            <BookOpen data-icon="inline-start" /> Skills library
          </Link>
        </Button>
        <Button asChild variant="ghost" className="workspace-settings-link">
          <Link href="/settings">
            <Settings2 data-icon="inline-start" />
            Settings
          </Link>
        </Button>
        <div>
          <span className="public-avatar">
            <Globe2 aria-hidden />
          </span>
          <span>
            <strong>Public demo workspace</strong>
            <small>Shared questions. Shared discoveries.</small>
          </span>
        </div>
        <span className="footer-note">
          <ShieldCheck aria-hidden />
          Read-only access to synthetic data
        </span>
      </div>
    </>
  );

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to conversation
      </a>
      <aside className="desktop-sidebar">{sidebar}</aside>
      <div className="workspace-main">
        <header className={cn("topbar", conversation && "topbar-conversation")}>
          <Sheet>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="mobile-menu"
                aria-label="Open workspace navigation"
              >
                <Menu />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="mobile-sidebar">
              <SheetTitle className="sr-only">Workspace navigation</SheetTitle>
              {sidebar}
            </SheetContent>
          </Sheet>
          <div className="breadcrumb">
            <Layers3 aria-hidden />
            <span>Retail workspace</span>
            <ChevronRight aria-hidden />
            <strong>{conversation ? "Exploration" : "Overview"}</strong>
          </div>
          <div className="topbar-actions">
            <Sheet>
              <SheetTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="data-sources-trigger"
                  aria-label="View data sources"
                >
                  <Database data-icon="inline-start" />
                  <span>Sources</span>
                </Button>
              </SheetTrigger>
              <SheetContent className="data-sources-panel">
                <SheetHeader>
                  <SheetTitle>Data sources</SheetTitle>
                  <SheetDescription>
                    Read-only connections to synthetic retail data. Choose which
                    sources to query in the composer.
                  </SheetDescription>
                </SheetHeader>
                <div className="data-sources-body">
                  <div className="source-list">
                    {loading ? (
                      <>
                        <Skeleton className="source-skeleton" />
                        <Skeleton className="source-skeleton" />
                      </>
                    ) : (
                      connections.map((connection) => (
                        <div key={connection.id}>
                          <button
                            type="button"
                            className="source-item"
                            aria-pressed={schemaSource === connection.id}
                            onClick={() => void openSchema(connection.id)}
                          >
                            <span
                              className={cn(
                                "database-icon",
                                connection.id === "postgres" &&
                                  "database-icon-teal",
                              )}
                            >
                              <Database aria-hidden />
                            </span>
                            <span>
                              <strong>{connection.engine}</strong>
                              <small>{connection.name}</small>
                              <span className="sr-only">
                                {connection.connected
                                  ? "Connected"
                                  : "Disconnected"}
                              </span>
                            </span>
                            <span
                              className={cn(
                                "connection-dot",
                                !connection.connected && "connection-dot-error",
                              )}
                              aria-hidden="true"
                            />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                  {!loading && !connections.length && (
                    <p className="source-empty">
                      No data sources are available.
                    </p>
                  )}
                  <div className="schema-content">
                    {schemaSource ? (
                      <h3>
                        {
                          connections.find(
                            (connection) => connection.id === schemaSource,
                          )?.name
                        }{" "}
                        schema
                      </h3>
                    ) : (
                      <p>
                        Choose a source above to inspect its tables and columns.
                      </p>
                    )}
                    {schemaError && (
                      <Alert variant="destructive">
                        <AlertDescription>{schemaError}</AlertDescription>
                      </Alert>
                    )}
                    {schemaLoading && <Skeleton className="result-loading" />}
                    {schemaSource &&
                      !schemaLoading &&
                      !schemaError &&
                      !schema.length && (
                        <p>No tables are available for this source.</p>
                      )}
                    {schema.map((table) => (
                      <details key={table.table}>
                        <summary>
                          <TableIcon />
                          {table.table}
                          <Badge variant="secondary">
                            {table.columns.length}
                          </Badge>
                        </summary>
                        <p>{table.description}</p>
                        <ul>
                          {table.columns.map((column) => (
                            <li key={column.name}>
                              <code>{column.name}</code>
                              <span>{column.type}</span>
                            </li>
                          ))}
                        </ul>
                      </details>
                    ))}
                  </div>
                </div>
              </SheetContent>
            </Sheet>
            <Button asChild variant="ghost" size="icon">
              <Link href="/settings" aria-label="Open settings">
                <Settings2 />
              </Link>
            </Button>
            <Badge variant="secondary">
              <Globe2 data-icon="inline-start" />
              Public
            </Badge>
            {conversation && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={forking}
                  onClick={() => void fork()}
                >
                  {forking ? (
                    <LoaderCircle className="spin" data-icon="inline-start" />
                  ) : (
                    <GitFork data-icon="inline-start" />
                  )}
                  Fork
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Copy conversation link"
                  onClick={async () => {
                    try {
                      await navigator.clipboard.writeText(
                        new URL(
                          workspacePath(conversation.id),
                          window.location.origin,
                        ).href,
                      );
                      toast.success("Public conversation link copied", {
                        id: "copy-conversation",
                      });
                    } catch {
                      toast.error("Could not copy the link.");
                    }
                  }}
                >
                  <Link2 />
                </Button>
              </>
            )}
            <Sheet>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="How this workspace works"
                >
                  <CircleHelp />
                </Button>
              </SheetTrigger>
              <SheetContent>
                <SheetHeader>
                  <SheetTitle>Your data, explained</SheetTitle>
                  <SheetDescription>
                    Ask a question, inspect the evidence, and keep exploring.
                  </SheetDescription>
                </SheetHeader>
                <div className="help-content">
                  <h2>Two sources, one conversation</h2>
                  <p>
                    BigQuery holds orders, products, and returns. PostgreSQL
                    holds customer profiles, revenue targets, and campaigns.
                  </p>
                  <h2>Every answer has evidence</h2>
                  <p>
                    Open SQL & evidence to inspect executed queries, source
                    timestamps, row counts, and assumptions. Inferred
                    relationships are labeled and checked for duplicate keys.
                  </p>
                  <h2>This workspace is public</h2>
                  <p>
                    All visitors can read conversations and ask follow-ups. Use
                    synthetic retail data only. Fork a chat to explore another
                    direction.
                  </p>
                  <h2>Talk naturally</h2>
                  <p>
                    Start voice to speak with Gemini. You can interrupt, mute,
                    or stop. Transcripts are saved; raw audio is not recorded.
                  </p>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </header>
        <main
          id="main-content"
          tabIndex={0}
          onPointerDown={() => {
            followLatest.current = false;
          }}
          onWheel={(event) => {
            if (event.deltaY < 0) followLatest.current = false;
          }}
          onTouchStart={() => {
            followLatest.current = false;
          }}
          onKeyDown={(event) => {
            if (["ArrowUp", "PageUp", "Home"].includes(event.key))
              followLatest.current = false;
          }}
          onScroll={(event) => {
            const node = event.currentTarget;
            followLatest.current =
              node.scrollHeight - node.scrollTop - node.clientHeight < 40;
          }}
        >
          <div className="workspace-content">
            {mode.includes("fixtures") && (
              <div className="local-mode">
                <Radio aria-hidden />
                {mode === "local-fixtures"
                  ? "Local sample mode · deterministic queries, no live AI calls"
                  : "Gemini preview · local synthetic fixtures · in-memory chats"}
              </div>
            )}
            {error && (
              <Alert variant="destructive" className="workspace-error">
                <AlertTitle>Could not complete that request</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Dismiss error"
                  onClick={() => setError("")}
                >
                  <X />
                </Button>
              </Alert>
            )}
            <AnimatePresence initial={false} mode="wait">
              {!conversation && !messages.length ? (
                <Reveal className="welcome" key="welcome" initial={false}>
                  <div className="welcome-eyebrow">
                    <span className="connection-dot" />
                    RETAIL INTELLIGENCE<span>{dataPeriod}</span>
                  </div>
                  <div className="welcome-heading">
                    <h1>
                      Your data has a story.
                      <br />
                      <span>Ask the next question.</span>
                    </h1>
                    <p>
                      Go from a question to a clear answer. Explore your
                      warehouse
                      <br className="desktop-break" /> and business data
                      together, with the evidence to back it up.
                    </p>
                  </div>
                  <div className="source-path">
                    <div className="path-source">
                      <span className="database-icon">
                        <Database aria-hidden />
                      </span>
                      <div>
                        <strong>BigQuery</strong>
                        <small>Sales & products</small>
                      </div>
                    </div>
                    <span className="path-line" aria-hidden />
                    <span className="path-junction">
                      <Mark small />
                    </span>
                    <span className="path-line" aria-hidden />
                    <div className="path-source">
                      <span className="database-icon database-icon-teal">
                        <Database aria-hidden />
                      </span>
                      <div>
                        <strong>PostgreSQL</strong>
                        <small>Customers & targets</small>
                      </div>
                    </div>
                  </div>
                  <div className="suggestions-label">
                    A GOOD QUESTION IS ALL IT TAKES
                    <ArrowDown aria-hidden />
                  </div>
                  <div className="suggestion-grid">
                    {suggestions.map((suggestion) => (
                      <motion.button
                        key={suggestion.title}
                        className="suggestion-card"
                        disabled={busy || loading}
                        onClick={() =>
                          void ask(suggestion.question, suggestion.sourceId)
                        }
                        whileHover={reduced ? undefined : { y: -3 }}
                        whileTap={reduced ? undefined : { scale: 0.985 }}
                        transition={SPRING_PRESS}
                      >
                        <suggestion.icon aria-hidden />
                        <strong>{suggestion.title}</strong>
                        <p>{suggestion.detail}</p>
                        <span>
                          {suggestion.source}
                          <ArrowRight aria-hidden />
                        </span>
                      </motion.button>
                    ))}
                  </div>
                  <div className="welcome-footnote">
                    <Check aria-hidden />
                    Read-only queries<span>·</span>
                    <Check aria-hidden />
                    Visible SQL & sources<span>·</span>
                    <Check aria-hidden />
                    Follow-up ready
                  </div>
                </Reveal>
              ) : (
                <Reveal
                  className="chat-content"
                  key={conversation?.id ?? "new-chat"}
                >
                  <div className="chat-heading">
                    <div className="welcome-eyebrow">PUBLIC EXPLORATION</div>
                    <h1>{conversation?.title ?? "New exploration"}</h1>
                    <p>
                      {source === "all"
                        ? "BigQuery + PostgreSQL"
                        : source === "bigquery"
                          ? "BigQuery"
                          : "PostgreSQL"}
                      <span>·</span>Synthetic retail data<span>·</span>Visible
                      to everyone
                    </p>
                  </div>
                  {messages.length === 0 && !busy && (
                    <Empty>
                      <EmptyHeader>
                        <EmptyTitle>Start this exploration</EmptyTitle>
                        <EmptyDescription>
                          Ask a retail question below, or start a live voice
                          conversation.
                        </EmptyDescription>
                      </EmptyHeader>
                    </Empty>
                  )}
                  <AnimatePresence initial={false}>
                    {messages.map((message) => (
                      <motion.article
                        key={message.id}
                        initial={
                          hydrated && !reduced ? { opacity: 0, y: 12 } : false
                        }
                        animate={{ opacity: 1, y: 0 }}
                        exit={reduced ? undefined : { opacity: 0 }}
                        transition={{
                          duration: reduced ? 0 : 0.24,
                          ease: EASE_OUT,
                        }}
                        className={cn(
                          "message",
                          message.role === "user"
                            ? "user-message"
                            : "assistant-message",
                        )}
                      >
                        <div className="message-label">
                          {message.role === "assistant" ? (
                            <>
                              <Mark small />
                              Querylane
                            </>
                          ) : (
                            <>
                              <span className="guest-dot" />
                              Guest question
                            </>
                          )}
                        </div>
                        <MessageContent
                          role={message.role}
                          className="message-text"
                        >
                          {message.text}
                        </MessageContent>
                        <SkillEvidence
                          skills={message.skills_used}
                          warnings={message.skill_warnings}
                        />
                        {message.artifact_id &&
                          artifacts[message.artifact_id] && (
                            <ResultCard
                              artifact={artifacts[message.artifact_id]}
                              onExplore={draftChartQuestion}
                            />
                          )}
                        {preferences.followups &&
                          Boolean(message.followups?.length) && (
                            <div className="followups">
                              {message.followups?.map((followup) => (
                                <Button
                                  key={followup}
                                  variant="outline"
                                  size="sm"
                                  disabled={busy}
                                  onClick={() => void ask(followup)}
                                >
                                  {followup}
                                  <ArrowRight data-icon="inline-end" />
                                </Button>
                              ))}
                            </div>
                          )}
                      </motion.article>
                    ))}
                  </AnimatePresence>
                  {draftArtifact &&
                    artifacts[draftArtifact] &&
                    !messages.some(
                      (message) => message.artifact_id === draftArtifact,
                    ) && (
                      <ResultCard
                        artifact={artifacts[draftArtifact]}
                        onExplore={draftChartQuestion}
                      />
                    )}
                  <AnimatePresence initial={false}>
                    {runId && (
                      <Reveal key="progress">
                        <AnalysisProgress
                          stage={stage}
                          message={
                            stopping
                              ? "Stopping the active analysis…"
                              : progress
                          }
                        />
                      </Reveal>
                    )}
                  </AnimatePresence>
                  {conversation && (
                    <ConversationReports
                      key={conversation.id}
                      conversationId={conversation.id}
                      refreshKey={reportRefresh}
                    />
                  )}
                  <div ref={registerBottom} />
                </Reveal>
              )}
            </AnimatePresence>
          </div>
        </main>
        <footer className="composer-area">
          <SkillAttachments
            conversation={conversation}
            source={conversation?.source ?? source}
            disabled={busy || loading}
            ensureConversation={ensureConversation}
            onSavingChange={setUpdatingSkills}
            onSaved={(chat) => {
              if (activeConversation.current === chat.id) setConversation(chat);
            }}
          />
          <AnimatePresence initial={false}>
            {voiceState !== "off" && (
              <Reveal className="voice-panel" key="voice-panel">
                <span className="voice-indicator">
                  <AudioLines aria-hidden />
                </span>
                <div className="voice-panel-text">
                  <strong>
                    {voiceState === "live"
                      ? "Live conversation"
                      : voiceState === "connecting"
                        ? "Connecting to Gemini…"
                        : "Voice paused"}
                  </strong>
                  <p>
                    {voiceText ||
                      "Ask naturally. Your charts and evidence will appear above."}
                  </p>
                </div>
                <div className="voice-level" aria-hidden>
                  {[0.4, 0.8, 0.6, 1, 0.7, 0.9, 0.5].map((factor, index) => (
                    <motion.i
                      key={index}
                      initial={false}
                      animate={{
                        scaleY: reduced ? 0.28 : 0.14 + level * factor * 0.86,
                      }}
                      style={{ height: 28 }}
                      transition={{
                        duration: reduced ? 0 : 0.08,
                        ease: "linear",
                      }}
                    />
                  ))}
                </div>
                {voiceState === "disconnected" ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => void startVoice()}
                  >
                    Reconnect
                  </Button>
                ) : (
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={muted ? "Unmute microphone" : "Mute microphone"}
                    aria-pressed={muted}
                    onClick={() => {
                      const next = voice.current?.toggleMute() ?? false;
                      setMuted(next);
                      toast.info(
                        next ? "Microphone muted" : "Microphone live",
                        { id: "voice-microphone", duration: 2500 },
                      );
                    }}
                  >
                    {muted ? <MicOff /> : <Mic />}
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Stop voice"
                  onClick={() => {
                    voice.current?.stop();
                    setVoiceState("off");
                    setMuted(false);
                    toast.info("Voice session ended", {
                      id: "voice-session",
                      description:
                        "Your transcripts and results remain in this conversation.",
                      duration: 4000,
                    });
                    if (conversation) void loadMessages(conversation.id);
                  }}
                >
                  <Square />
                </Button>
              </Reveal>
            )}
          </AnimatePresence>
          <form
            className="composer"
            onSubmit={(event) => {
              event.preventDefault();
              void ask();
            }}
          >
            <Field>
              <FieldLabel className="sr-only" htmlFor="question">
                Ask a question about retail data
              </FieldLabel>
              <InputGroup>
                <InputGroupTextarea
                  ref={input}
                  id="question"
                  placeholder="Ask anything about your retail data…"
                  value={question}
                  maxLength={4000}
                  disabled={busy}
                  rows={2}
                  aria-describedby="public-chat-hint"
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      (event.ctrlKey ||
                        event.metaKey ||
                        (preferences.enterToSend && !event.shiftKey)) &&
                      !event.nativeEvent.isComposing
                    ) {
                      event.preventDefault();
                      void ask();
                    }
                  }}
                />
                <InputGroupAddon align="block-end">
                  <Select
                    value={source}
                    disabled={busy || Boolean(conversation)}
                    onValueChange={(value) => {
                      setSource(value);
                      toast.info("Data source selected", {
                        id: "source-selection",
                        description: `${value === "all" ? "BigQuery and PostgreSQL" : value === "bigquery" ? "BigQuery" : "PostgreSQL"} will be used for this exploration.`,
                        duration: 3000,
                      });
                    }}
                  >
                    <SelectTrigger aria-label="Data sources for new exploration">
                      <Database aria-hidden />
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        <SelectItem value="all">All sources</SelectItem>
                        <SelectItem value="bigquery">BigQuery</SelectItem>
                        <SelectItem value="postgres">PostgreSQL</SelectItem>
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                  <span className="composer-spacer" />
                  {reportsEnabled && (
                    <InputGroupButton
                      size="sm"
                      aria-pressed={advanced}
                      disabled={busy || loading}
                      onClick={() => setAdvanced((v) => !v)}
                      className={advanced ? "advanced-active" : undefined}
                    >
                      <FileChartColumn aria-hidden />
                      <span>Advanced Analysis</span>
                    </InputGroupButton>
                  )}
                  {advanced && (
                    <Select
                      value={reportStyle}
                      onValueChange={(v) =>
                        setReportStyle(v as "business" | "technical")
                      }
                    >
                      <SelectTrigger aria-label="Report style">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectItem value="business">
                            Business report
                          </SelectItem>
                          <SelectItem value="technical">
                            Technical report
                          </SelectItem>
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  )}

                  <InputGroupButton
                    size="sm"
                    aria-label="Start live voice conversation"
                    disabled={busy || loading}
                    onClick={() => void startVoice()}
                  >
                    <AudioLines data-icon="inline-start" />
                    <span>Voice</span>
                  </InputGroupButton>
                  {runId ? (
                    <InputGroupButton
                      size="icon-sm"
                      aria-label="Stop analysis"
                      disabled={stopping}
                      onClick={() => void cancelAnalysis()}
                    >
                      {stopping ? (
                        <LoaderCircle className="spin" />
                      ) : (
                        <Square />
                      )}
                    </InputGroupButton>
                  ) : (
                    <InputGroupButton
                      size={advanced ? "sm" : "icon-sm"}
                      variant="default"
                      type="submit"
                      aria-label={advanced ? "Create report" : "Send question"}
                      disabled={busy || !question.trim() || loading}
                    >
                      {starting ? (
                        <LoaderCircle className="spin" />
                      ) : (
                        <ArrowUp />
                      )}
                      {advanced && <span>Create report</span>}
                    </InputGroupButton>
                  )}
                </InputGroupAddon>
              </InputGroup>
            </Field>
          </form>
          {advanced && (
            <p className="advanced-hint">
              Public detailed report · typically 3–8 minutes · clarifies only
              essential details. Chat stays available.
            </p>
          )}
          <div className="composer-hint" id="public-chat-hint">
            <span>
              <Globe2 aria-hidden />
              Public workspace. Questions and answers are visible to everyone.
            </span>
            <span>
              <Command aria-hidden />
              {preferences.enterToSend
                ? "Enter to send · Shift + Enter for a new line"
                : "Ctrl / ⌘ + Enter to send · Enter for a new line"}
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}

function TableIcon() {
  return <Database aria-hidden />;
}
