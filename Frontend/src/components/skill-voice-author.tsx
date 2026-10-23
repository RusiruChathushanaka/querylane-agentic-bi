"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import Link from "@/components/ui/app-link";
import {
  ArrowUpRight,
  Check,
  Circle,
  LoaderCircle,
  Mic,
  MicOff,
  Send,
  Square,
  Volume2,
} from "lucide-react";
import { toast } from "sonner";
import { guestApi } from "@/lib/api";
import { LiveVoice, type VoiceEvent } from "@/lib/voice";
import type { AuthorSession, Skill, SkillContent } from "@/lib/types";
import { usePreferences } from "@/hooks/use-preferences";
import { useAppMotion } from "@/hooks/use-app-motion";
import { SkillMarkdown } from "@/components/skill-markdown";
import { MessageContent } from "@/components/markdown-content";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const STORAGE_KEY = "querylane-skill-author-session-v1";
const requirements = [
  ["purpose", "Purpose"],
  ["when_to_use", "When to use"],
  ["source", "Data sources"],
  ["workflow", "Workflow"],
  ["definitions", "Business definitions"],
  ["examples", "Examples"],
] as const;
const path = (id: string) => `/skills/author-sessions/${id}`;
async function loadSavedInterview() {
  const id = sessionStorage.getItem(STORAGE_KEY);
  return id ? guestApi<AuthorSession>(path(id)) : null;
}

type Phase = "off" | "connecting" | "live" | "pausing";

export function SkillVoiceAuthor({
  open,
  onOpenChange,
  onPublished,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onPublished: () => void;
}) {
  const { preferences } = usePreferences();
  const { reduced } = useAppMotion();
  const [session, setSession] = useState<AuthorSession | null>(null);
  const [draft, setDraft] = useState<SkillContent | null>(null);
  const [phase, setPhase] = useState<Phase>("off");
  const [tab, setTab] = useState("conversation");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [muted, setMuted] = useState(false);
  const [textOnly, setTextOnly] = useState(false);
  const [level, setLevel] = useState(0);
  const [reply, setReply] = useState("");
  const [partial, setPartial] = useState({ user: "", assistant: "" });
  const [accepted, setAccepted] = useState(false);
  const [invalidField, setInvalidField] = useState("");
  const [announcement, setAnnouncement] = useState("");
  const [discard, setDiscard] = useState(false);
  const [newInterview, setNewInterview] = useState(false);
  const voice = useRef<LiveVoice | null>(null);
  const attempt = useRef<string | null>(null);
  const reviewAfterPause = useRef(false);
  const connection = useRef(0);
  const transcript = useRef<HTMLDivElement>(null);
  const follow = useRef(true);
  const dirty = Boolean(
    draft &&
      session?.draft &&
      JSON.stringify(draft) !== JSON.stringify(session.draft),
  );
  const connected = phase !== "off";
  const published = Boolean(session?.published_skill_id);

  const apply = useCallback((value: AuthorSession) => {
    setSession(value);
    setDraft(value.draft);
    setAccepted(false);
  }, []);

  const recover = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const saved = await loadSavedInterview();
      if (saved) apply(saved);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "The saved interview could not be recovered.",
      );
    } finally {
      setLoading(false);
    }
  }, [apply]);

  const disconnect = useCallback(() => {
    connection.current++;
    voice.current?.stop();
    voice.current = null;
  }, []);

  useEffect(() => {
    let active = true;
    if (open) {
      void loadSavedInterview()
        .then((saved) => {
          if (active && saved) apply(saved);
        })
        .catch((err: unknown) => {
          if (active)
            setError(
              err instanceof Error
                ? err.message
                : "The saved interview is unavailable.",
            );
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }
    return () => {
      active = false;
      disconnect();
    };
  }, [open, apply, disconnect]);

  useEffect(() => {
    if (!dirty) return;
    const warn = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);

  useEffect(() => {
    if (follow.current && transcript.current)
      transcript.current.scrollTop = transcript.current.scrollHeight;
  }, [partial, session?.transcript.length]);

  function reset() {
    connection.current++;
    voice.current?.stop();
    voice.current = null;
    sessionStorage.removeItem(STORAGE_KEY);
    attempt.current = null;
    setSession(null);
    setDraft(null);
    setPhase("off");
    setTab("conversation");
    setError("");
    setReply("");
    setPartial({ user: "", assistant: "" });
    setAccepted(false);
    setNewInterview(false);
  }

  function close() {
    if (saving) return;
    if (dirty) {
      setDiscard(true);
      return;
    }
    connection.current++;
    voice.current?.stop();
    voice.current = null;
    setPhase("off");
    setLoading(true);
    setPartial({ user: "", assistant: "" });
    onOpenChange(false);
  }

  async function connect(typing = false) {
    if (connected || saving || dirty) return;
    const generation = ++connection.current;
    setPhase("connecting");
    setError("");
    setTextOnly(typing);
    setTab("conversation");
    setPartial({ user: "", assistant: "" });
    reviewAfterPause.current = false;
    toast.loading("Connecting skill author…", {
      id: "skill-author-connection",
    });
    try {
      let current = session;
      if (!current) {
        attempt.current ??= crypto.randomUUID();
        current = await guestApi<AuthorSession>("/skills/author-sessions", {
          method: "POST",
          body: JSON.stringify({ idempotency_key: attempt.current }),
        });
        sessionStorage.setItem(STORAGE_KEY, current.id);
        apply(current);
      }
      if (generation !== connection.current) return;
      const id = current.id;
      let finalSnapshotReceived = false;
      const client = new LiveVoice(
        (event: VoiceEvent) => {
          if (generation !== connection.current) return;
          if (event.session) {
            apply(event.session as AuthorSession);
            if (event.type === "stopped") finalSnapshotReceived = true;
          }
          if (event.type === "ready") {
            setPhase("live");
            setMuted(typing || preferences.startMuted);
            setAnnouncement(
              "Skill author connected. Describe the analytics task you want to teach.",
            );
            toast.success("Skill author connected", {
              id: "skill-author-connection",
              description: typing
                ? "Type your replies below."
                : "Speak naturally; you can interrupt to correct details.",
            });
          } else if (event.type === "transcript") {
            const role = event.role === "user" ? "user" : "assistant";
            setPartial((value) => ({
              ...value,
              [role]: event.replace
                ? String(event.text ?? "")
                : value[role] + String(event.text ?? ""),
            }));
          } else if (event.type === "user_message") {
            setPartial((value) => ({
              ...value,
              user: String(event.text ?? ""),
            }));
          } else if (event.type === "turn_complete") {
            setPartial({ user: "", assistant: "" });
            setAnnouncement(
              "The assistant finished its reply. Your interview is saved.",
            );
          } else if (event.type === "draft") {
            setAnnouncement(
              "Your skill draft is ready. Pause the assistant to review and publish.",
            );
            toast.success("Skill draft ready", {
              id: "skill-author-draft",
              description:
                "Pause to review the draft. Nothing has been published.",
            });
          } else if (event.type === "interrupted") {
            setPartial({ user: "", assistant: "" });
            setAnnouncement(
              "Assistant interrupted. Continue with your correction.",
            );
          } else if (
            ["error", "session_limit", "reconnect"].includes(event.type)
          ) {
            const message = String(
              event.message ?? "Reconnect to continue your saved interview.",
            );
            setError(message);
            setPhase("off");
            client.stop();
            toast.error("Skill author paused", {
              id: "skill-author-connection",
              description: message,
            });
          } else if (
            event.type === "stopped" ||
            event.type === "disconnected"
          ) {
            setPhase("off");
            if (reviewAfterPause.current) setTab("review");
            if (event.type === "disconnected") {
              setError(
                "Connection ended. Your committed requirements and draft are saved. Reconnect to continue.",
              );
              toast.info("Skill interview saved", {
                id: "skill-author-connection",
                description: "Reconnect to continue.",
              });
            }
            if (!event.session && !finalSnapshotReceived) {
              setPhase("pausing");
              void guestApi<AuthorSession>(path(id))
                .then((value) => {
                  if (generation === connection.current) apply(value);
                })
                .catch(() => {})
                .finally(() => {
                  if (generation === connection.current) setPhase("off");
                });
            }
          }
        },
        setLevel,
        {
          spokenResponses: preferences.spokenResponses,
          startMuted: preferences.startMuted,
          endpoint: `/api/v1${path(id)}/voice`,
          textOnly: typing,
        },
      );
      voice.current = client;
      await client.start(id);
      if (generation !== connection.current) client.stop();
    } catch (err) {
      if (generation !== connection.current) return;
      voice.current?.stop();
      setPhase("off");
      const message =
        err instanceof Error
          ? err.message
          : "Could not connect the voice author.";
      setError(message);
      toast.error("Could not start voice", {
        id: "skill-author-connection",
        description:
          "Allow microphone access or continue with typing. " + message,
      });
    }
  }

  function pause(review = false) {
    if (phase === "connecting") {
      // Cancel HTTP setup, pending microphone permission, and late ready events.
      connection.current++;
      voice.current?.stop();
      voice.current = null;
      setPhase("off");
      toast.dismiss("skill-author-connection");
      if (review) setTab("review");
      return;
    }
    if (phase === "off") {
      if (review) setTab("review");
      return;
    }
    reviewAfterPause.current = review;
    setPhase("pausing");
    voice.current?.stop(true);
    toast.dismiss("skill-author-connection");
  }

  function send(event: FormEvent) {
    event.preventDefault();
    if (reply.trim() && voice.current?.sendText(reply.trim())) {
      setReply("");
      follow.current = true;
    }
  }

  function edit<K extends keyof SkillContent>(key: K, value: SkillContent[K]) {
    setDraft((previous) =>
      previous ? { ...previous, [key]: value } : previous,
    );
    setAccepted(false);
    setInvalidField("");
  }

  async function saveReview() {
    if (!session || !draft) return null;
    const content = {
      ...draft,
      tags: draft.tags.map((tag) => tag.trim()).filter(Boolean),
    };
    for (const key of [
      "name",
      "description",
      "when_to_use",
      "instructions",
    ] as const) {
      if (!content[key].trim()) {
        setInvalidField(key);
        throw new Error(
          `Enter ${key.replaceAll("_", " ")} before saving the draft.`,
        );
      }
    }
    if (new TextEncoder().encode(content.instructions).length > 16384) {
      setInvalidField("instructions");
      throw new Error("Instructions must fit within 16 KiB of UTF-8 text.");
    }
    if (
      content.tags.length > 8 ||
      content.tags.some((tag) => Array.from(tag).length > 30)
    ) {
      setInvalidField("tags");
      throw new Error(
        "Use up to eight tags, each no longer than 30 characters.",
      );
    }
    const value = await guestApi<AuthorSession>(`${path(session.id)}/draft`, {
      method: "PATCH",
      body: JSON.stringify({
        expected_revision: session.revision,
        content,
      }),
    });
    apply(value);
    return value;
  }

  async function publish() {
    if (!session || !draft || saving || connected || !accepted) return;
    setSaving(true);
    setError("");
    try {
      const current = dirty ? await saveReview() : session;
      if (!current) return;
      const skill = await guestApi<Skill>(`${path(current.id)}/publish`, {
        method: "POST",
        body: JSON.stringify({ expected_revision: current.revision }),
      });
      setSession((value) =>
        value
          ? { ...value, status: "published", published_skill_id: skill.id }
          : value,
      );
      toast.success("Voice-authored skill published", {
        description:
          skill.deleted || !skill.enabled
            ? "This skill's status has since changed in the shared library."
            : "The agent can now discover it in the shared library.",
      });
      onPublished();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Publication failed. Your draft is still available.",
      );
      toast.error("Skill was not published", {
        description: "Your draft is preserved. Resolve the error and retry.",
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(value) => {
          if (!value) close();
        }}
      >
        <DialogContent
          className="skill-author-dialog"
          onInteractOutside={(event) => {
            if (connected || saving) event.preventDefault();
          }}
        >
          <DialogHeader>
            <DialogTitle>
              Build a skill, in conversation
              <span className="text-primary">.</span>
            </DialogTitle>
            <DialogDescription>
              Tell your assistant how the business works. Refine the playbook
              together, then review and publish it for everyone.
            </DialogDescription>
          </DialogHeader>
          <p className="skill-author-privacy">
            Transcripts and drafts are saved for recovery with this guest
            browser session. Raw audio is not recorded. Avoid secrets and
            private information.
          </p>
          {loading ? (
            <p role="status">Recovering your interview…</p>
          ) : published ? (
            <div className="skill-author-success">
              <Check aria-hidden />
              <h3>Your skill is in the library.</h3>
              <p>
                It is available to the agent through the same versioned skills
                system.
              </p>
              <Button asChild>
                <Link
                  href={`/skills/${session!.published_skill_id}/revisions/1`}
                >
                  View published version <ArrowUpRight aria-hidden />
                </Link>
              </Button>
              <Button variant="outline" onClick={reset}>
                Start another interview
              </Button>
            </div>
          ) : (
            <Tabs
              value={tab}
              onValueChange={(value) => {
                if (value === "review") pause(true);
                else setTab(value);
              }}
            >
              <TabsList aria-label="Skill author workspace">
                <TabsTrigger value="conversation">Conversation</TabsTrigger>
                <TabsTrigger value="review" disabled={!session?.draft}>
                  Review draft{" "}
                  {session?.draft ? (
                    <Badge variant="secondary">Ready</Badge>
                  ) : null}
                </TabsTrigger>
              </TabsList>
              <TabsContent
                value="conversation"
                className="skill-author-conversation"
              >
                <div className="skill-author-brief">
                  <p className="skill-author-label">
                    YOUR PLAYBOOK, TAKING SHAPE
                  </p>
                  <ul className="skill-author-checklist">
                    {requirements.map(([key, label]) => (
                      <li
                        key={key}
                        data-complete={Boolean(session?.brief[key])}
                      >
                        {session?.brief[key] ? (
                          <Check aria-hidden />
                        ) : (
                          <Circle aria-hidden />
                        )}{" "}
                        <span>{label}</span>
                        <span className="sr-only">
                          {session?.brief[key]
                            ? ": captured"
                            : ": still to discuss"}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <p>
                    {session?.draft
                      ? "A draft is ready. Pause to review it, or keep talking to refine the details."
                      : "The assistant will ask about missing details. A draft is prepared once these six areas are clear."}
                  </p>
                </div>
                <div
                  className="skill-author-transcript"
                  ref={transcript}
                  tabIndex={0}
                  role="log"
                  aria-label="Skill interview transcript"
                  aria-live="off"
                  onScroll={() => {
                    const node = transcript.current;
                    if (node)
                      follow.current =
                        node.scrollHeight - node.scrollTop - node.clientHeight <
                        90;
                  }}
                >
                  {!session?.transcript.length && !partial.assistant && (
                    <div className="skill-author-welcome">
                      <Volume2 aria-hidden />
                      <h3>Start with the task you want to teach.</h3>
                      <p>
                        “Help our team compare regional sales with targets.”
                        Your assistant will ask about sources, definitions, and
                        examples before writing the skill.
                      </p>
                    </div>
                  )}
                  {session?.transcript.map((message, index) => (
                    <div
                      className="skill-author-message"
                      data-role={message.role}
                      key={`${message.created_at}-${index}`}
                    >
                      <strong>
                        {message.role === "user" ? "You" : "Skill assistant"}
                      </strong>
                      <MessageContent role={message.role}>{message.text}</MessageContent>
                    </div>
                  ))}
                  {(["user", "assistant"] as const).map((role) =>
                    partial[role] ? (
                      <div
                        className="skill-author-message"
                        data-role={role}
                        key={role}
                      >
                        <strong>
                          {role === "user"
                            ? "You · speaking"
                            : "Skill assistant · speaking"}
                        </strong>
                        <MessageContent role={role}>{partial[role]}</MessageContent>
                      </div>
                    ) : null,
                  )}
                </div>
                <div className="skill-author-controls">
                  <div className="skill-author-connection">
                    <Badge variant={phase === "live" ? "default" : "secondary"}>
                      {phase === "live"
                        ? textOnly
                          ? "Connected · typing"
                          : muted
                            ? "Microphone muted"
                            : "Listening"
                        : phase === "connecting"
                          ? "Connecting…"
                          : phase === "pausing"
                            ? "Saving interview…"
                            : "Not connected"}
                    </Badge>
                    <div className="skill-author-meter" aria-hidden>
                      {Array.from({ length: 9 }, (_, index) => (
                        <span
                          key={index}
                          style={{
                            transform: `scaleY(${reduced || muted || phase !== "live" || textOnly ? 0.18 : 0.18 + level * (0.4 + (index % 4) * 0.2)})`,
                          }}
                        />
                      ))}
                    </div>
                  </div>
                  {dirty && (
                    <p className="skill-author-privacy">
                      Save your review edits in Review draft before
                      reconnecting.
                    </p>
                  )}
                  {phase === "off" ? (
                    <div className="skill-author-start-actions">
                      <Button
                        onClick={() => void connect()}
                        disabled={Boolean(session?.connected) || dirty}
                      >
                        <Mic aria-hidden />{" "}
                        {session
                          ? "Reconnect with voice"
                          : "Start voice interview"}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => void connect(true)}
                        disabled={Boolean(session?.connected) || dirty}
                      >
                        Continue with typing
                      </Button>
                    </div>
                  ) : (
                    <div className="skill-author-start-actions">
                      {!textOnly && (
                        <Button
                          variant="outline"
                          disabled={phase !== "live"}
                          onClick={() => {
                            const value = voice.current?.toggleMute() ?? true;
                            setMuted(value);
                            toast.info(
                              value
                                ? "Author microphone muted"
                                : "Author microphone on",
                              { id: "skill-author-mute" },
                            );
                          }}
                          aria-pressed={muted}
                        >
                          {muted ? <MicOff aria-hidden /> : <Mic aria-hidden />}
                          {muted ? "Unmute" : "Mute"}
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        disabled={phase === "pausing"}
                        onClick={() => pause()}
                      >
                        <Square aria-hidden /> Pause assistant
                      </Button>
                    </div>
                  )}
                  <form onSubmit={send}>
                    <FieldGroup>
                      <Field>
                        <FieldLabel htmlFor="skill-author-reply">
                          Reply by typing
                        </FieldLabel>
                        <div className="skill-author-reply">
                          <Input
                            id="skill-author-reply"
                            value={reply}
                            onChange={(event) => setReply(event.target.value)}
                            maxLength={4000}
                            placeholder="Add details or correct the assistant…"
                            disabled={phase !== "live"}
                          />
                          <Button
                            type="submit"
                            disabled={phase !== "live" || !reply.trim()}
                            aria-label="Send interview reply"
                          >
                            <Send aria-hidden />
                          </Button>
                        </div>
                      </Field>
                    </FieldGroup>
                  </form>
                  {session?.draft && (
                    <Button
                      variant="secondary"
                      onClick={() => pause(true)}
                      disabled={phase === "pausing"}
                    >
                      Review and publish draft <ArrowUpRight aria-hidden />
                    </Button>
                  )}
                </div>
              </TabsContent>
              <TabsContent value="review" className="skill-author-review">
                {draft && (
                  <>
                    <p>
                      Review the exact instructions the agent will receive.
                      Edits stay unpublished until you publish.
                    </p>
                    <FieldGroup>
                      <Field data-invalid={invalidField === "name"}>
                        <FieldLabel htmlFor="voice-skill-name">Name</FieldLabel>
                        <Input
                          aria-invalid={invalidField === "name"}
                          id="voice-skill-name"
                          value={draft.name}
                          maxLength={80}
                          required
                          disabled={connected || saving}
                          onChange={(event) => edit("name", event.target.value)}
                        />
                      </Field>
                      <Field data-invalid={invalidField === "description"}>
                        <FieldLabel htmlFor="voice-skill-description">
                          Description
                        </FieldLabel>
                        <Textarea
                          aria-invalid={invalidField === "description"}
                          id="voice-skill-description"
                          value={draft.description}
                          maxLength={300}
                          required
                          disabled={connected || saving}
                          onChange={(event) =>
                            edit("description", event.target.value)
                          }
                        />
                      </Field>
                      <Field data-invalid={invalidField === "when_to_use"}>
                        <FieldLabel htmlFor="voice-skill-when">
                          When to use
                        </FieldLabel>
                        <Textarea
                          aria-invalid={invalidField === "when_to_use"}
                          id="voice-skill-when"
                          value={draft.when_to_use}
                          maxLength={500}
                          required
                          disabled={connected || saving}
                          onChange={(event) =>
                            edit("when_to_use", event.target.value)
                          }
                        />
                      </Field>
                      <div className="skill-editor-pair">
                        <Field>
                          <FieldLabel htmlFor="voice-skill-source">
                            Source compatibility
                          </FieldLabel>
                          <Select
                            value={draft.source}
                            disabled={connected || saving}
                            onValueChange={(value) =>
                              edit("source", value as SkillContent["source"])
                            }
                          >
                            <SelectTrigger id="voice-skill-source">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectGroup>
                                <SelectItem value="all">All sources</SelectItem>
                                <SelectItem value="bigquery">
                                  BigQuery
                                </SelectItem>
                                <SelectItem value="postgres">
                                  PostgreSQL
                                </SelectItem>
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                        </Field>
                        <Field data-invalid={invalidField === "tags"}>
                          <FieldLabel htmlFor="voice-skill-tags">
                            Tags
                          </FieldLabel>
                          <Input
                            aria-invalid={invalidField === "tags"}
                            id="voice-skill-tags"
                            value={draft.tags.join(", ")}
                            disabled={connected || saving}
                            onChange={(event) =>
                              edit(
                                "tags",
                                event.target.value
                                  .split(",")
                                  .map((tag) => tag.trim()),
                              )
                            }
                          />
                          <FieldDescription>
                            Up to eight comma-separated tags.
                          </FieldDescription>
                        </Field>
                      </div>
                      <Field data-invalid={invalidField === "instructions"}>
                        <FieldLabel htmlFor="voice-skill-instructions">
                          Markdown instructions
                        </FieldLabel>
                        <Textarea
                          className="skill-author-instructions"
                          aria-invalid={invalidField === "instructions"}
                          id="voice-skill-instructions"
                          value={draft.instructions}
                          disabled={connected || saving}
                          required
                          onChange={(event) =>
                            edit("instructions", event.target.value)
                          }
                        />
                        <FieldDescription>
                          Maximum 16 KiB. Review metric definitions, filters,
                          and source assumptions.
                        </FieldDescription>
                      </Field>
                    </FieldGroup>
                    <div className="skill-author-preview" tabIndex={0}>
                      <h3>Markdown preview</h3>
                      <SkillMarkdown>{draft.instructions}</SkillMarkdown>
                    </div>
                    <Field orientation="horizontal">
                      <Checkbox
                        id="voice-skill-accept"
                        checked={accepted}
                        disabled={connected || saving}
                        onCheckedChange={(value) => setAccepted(value === true)}
                      />
                      <FieldLabel htmlFor="voice-skill-accept">
                        I reviewed this draft and want to publish it publicly.
                        Anyone can use, edit, or delete the skill.
                      </FieldLabel>
                    </Field>
                    <div className="skill-author-publish-actions">
                      <Button
                        variant="outline"
                        disabled={saving || connected}
                        onClick={async () => {
                          setSaving(true);
                          setError("");
                          try {
                            await saveReview();
                            setTab("conversation");
                            toast.success("Review edits saved", {
                              description:
                                "Continue the conversation to refine the brief; a regenerated draft can replace manual edits.",
                            });
                          } catch (err) {
                            setError(
                              err instanceof Error
                                ? err.message
                                : "Could not save review edits.",
                            );
                          } finally {
                            setSaving(false);
                          }
                        }}
                      >
                        Save edits and continue
                      </Button>
                      <Button
                        onClick={() => void publish()}
                        disabled={!accepted || saving || connected}
                      >
                        {saving ? (
                          <LoaderCircle className="spin" aria-hidden />
                        ) : (
                          <Check aria-hidden />
                        )}
                        {saving ? "Publishing…" : "Publish skill"}
                      </Button>
                    </div>
                  </>
                )}
              </TabsContent>
            </Tabs>
          )}
          {error && (
            <Alert variant="destructive">
              <AlertTitle>Skill author needs attention</AlertTitle>
              <AlertDescription>
                <p>{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={connected || saving}
                  onClick={() => {
                    if (
                      !dirty ||
                      window.confirm(
                        "Replace unsaved review edits with the saved draft?",
                      )
                    )
                      void recover();
                  }}
                >
                  Reload saved interview
                </Button>
              </AlertDescription>
            </Alert>
          )}
          <p role="status" className="sr-only">
            {announcement}
          </p>
          <DialogFooter>
            <Button
              variant="ghost"
              onClick={() => setNewInterview(true)}
              disabled={connected || saving || loading}
            >
              New interview
            </Button>
            <Button variant="outline" disabled={saving} onClick={close}>
              Close · keep saved draft
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog
        open={discard || newInterview}
        onOpenChange={(value) => {
          if (!value) {
            setDiscard(false);
            setNewInterview(false);
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {newInterview
                ? "Start a new interview?"
                : "Discard unsaved review edits?"}
            </DialogTitle>
            <DialogDescription>
              {newInterview
                ? "The saved interview is not deleted, but this browser will stop resuming it. Any unsaved review edits will be lost."
                : "The last saved draft remains available. Your unsaved review edits will be lost."}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDiscard(false);
                setNewInterview(false);
              }}
            >
              Keep working
            </Button>
            <Button
              onClick={() => {
                if (newInterview) reset();
                else {
                  setDraft(session?.draft ?? null);
                  setDiscard(false);
                  voice.current?.stop();
                  setPhase("off");
                  onOpenChange(false);
                }
              }}
            >
              {newInterview ? "Start new interview" : "Discard edits and close"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
