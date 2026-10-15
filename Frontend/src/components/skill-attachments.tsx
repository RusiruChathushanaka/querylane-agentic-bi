"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { BookOpen, Check, X } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { Conversation, SkillSummary } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

export function SkillAttachments({
  conversation,
  source,
  disabled,
  ensureConversation,
  onSaved,
  onSavingChange,
}: {
  conversation: Conversation | null;
  source: string;
  disabled: boolean;
  ensureConversation: () => Promise<Conversation>;
  onSaved: (chat: Conversation) => void;
  onSavingChange: (saving: boolean) => void;
}) {
  const [open, setOpen] = useState(false);
  const [skills, setSkills] = useState<SkillSummary[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [base, setBase] = useState<Conversation | null>(null);
  const ids = conversation?.skill_ids ?? [];
  const attachedKey = ids.join(",");
  useEffect(() => {
    let current = true;
    if (attachedKey)
      void Promise.all(
        attachedKey
          .split(",")
          .map((id) => api<SkillSummary>(`/skills/${id}`).catch(() => null)),
      ).then((values) => {
        if (current)
          setSkills((previous) => [
            ...previous.filter((s) => !values.some((v) => v?.id === s.id)),
            ...values.filter((s): s is SkillSummary => s !== null),
          ]);
      });
    return () => {
      current = false;
    };
  }, [attachedKey]);
  async function load() {
    setLoading(true);
    setError("");
    try {
      const [library, chat] = await Promise.all([
        api<{ skills: SkillSummary[] }>("/skills"),
        conversation
          ? api<{ conversation: Conversation }>(
              `/conversations/${conversation.id}`,
            ).then((r) => r.conversation)
          : Promise.resolve(null),
      ]);
      const attached = chat?.skill_ids ?? [];
      const missing = await Promise.all(
        attached
          .filter((id) => !library.skills.some((s) => s.id === id))
          .map((id) => api<SkillSummary>(`/skills/${id}`).catch(() => null)),
      );
      setSkills([
        ...library.skills,
        ...missing.filter((s): s is SkillSummary => s !== null),
      ]);
      setBase(chat);
      setSelected(attached);
      if (chat) onSaved(chat);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Skills are unavailable.");
    } finally {
      setLoading(false);
    }
  }
  async function save(next: string[], chatOverride?: Conversation | null) {
    setSaving(true);
    onSavingChange(true);
    setError("");
    try {
      const chat =
        chatOverride ?? base ?? conversation ?? (await ensureConversation());
      const result = await api<Conversation>(
        `/conversations/${chat.id}/skills`,
        {
          method: "PATCH",
          body: JSON.stringify({
            skill_ids: next,
            expected_revision: chat.skills_revision ?? 0,
          }),
        },
      );
      onSaved(result);
      setBase(result);
      setOpen(false);
      toast.success(
        next.length ? "Chat skills updated" : "Manual skills removed",
        {
          description:
            "Automatic discovery remains available for relevant skills.",
        },
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not update chat skills.",
      );
    } finally {
      setSaving(false);
      onSavingChange(false);
    }
  }
  return (
    <div className="skill-attachment-bar">
      <Button
        variant="ghost"
        size="sm"
        disabled={disabled}
        onClick={() => {
          setOpen(true);
          setSearch("");
          void load();
        }}
      >
        <BookOpen aria-hidden /> Attach skills{" "}
        {ids.length > 0 && <span>({ids.length}/3)</span>}
      </Button>
      {ids.map((id) => (
        <span key={id} className="skill-attachment-chip">
          {skills.find((s) => s.id === id)?.name ?? "Attached skill"}
          <Button
            variant="ghost"
            size="icon-sm"
            disabled={disabled || saving}
            aria-label={`Remove ${skills.find((s) => s.id === id)?.name ?? "attached skill"}`}
            onClick={() => {
              void save(
                ids.filter((key) => key !== id),
                conversation,
              );
            }}
          >
            <X aria-hidden />
          </Button>
        </span>
      ))}
      {skills.some(
        (skill) =>
          ids.includes(skill.id) &&
          (!skill.enabled ||
            skill.deleted ||
            !(
              source === "all" ||
              skill.source === "all" ||
              skill.source === source
            )),
      ) && (
        <p role="status">
          An attached skill is unavailable for this source. Remove it in Attach
          skills before asking another question.
        </p>
      )}
      {error && !open && <p role="alert">{error}</p>}
      <Dialog
        open={open}
        onOpenChange={(value) => {
          if (!saving) setOpen(value);
        }}
      >
        <DialogContent className="skill-attachment-dialog">
          <DialogHeader>
            <DialogTitle>Attach skills to this chat</DialogTitle>
            <DialogDescription>
              Choose up to three. Attachments are shared with everyone in this
              conversation. The agent also discovers relevant skills
              automatically.
            </DialogDescription>
          </DialogHeader>
          <Input
            aria-label="Search skills to attach"
            placeholder="Find a skill…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          {loading ? (
            <p>Loading skills…</p>
          ) : (
            <ul className="skill-attachment-list">
              {skills
                .filter((s) =>
                  `${s.name} ${s.description}`
                    .toLowerCase()
                    .includes(search.toLowerCase()),
                )
                .map((skill) => {
                  const checked = selected.includes(skill.id);
                  const available =
                    skill.enabled &&
                    !skill.deleted &&
                    (source === "all" ||
                      skill.source === "all" ||
                      skill.source === source);
                  return (
                    <li key={skill.id}>
                      <Button
                        variant={checked ? "secondary" : "ghost"}
                        aria-pressed={checked}
                        disabled={
                          saving ||
                          (!checked && (!available || selected.length >= 3))
                        }
                        onClick={() =>
                          setSelected(
                            checked
                              ? selected.filter((id) => id !== skill.id)
                              : [...selected, skill.id],
                          )
                        }
                      >
                        <span>
                          <strong>{skill.name}</strong>
                          <small>
                            {available
                              ? skill.description
                              : skill.deleted
                                ? "Deleted — remove this attachment"
                                : !skill.enabled
                                  ? "Disabled — remove this attachment"
                                  : "Incompatible source — remove this attachment"}
                          </small>
                        </span>
                        {checked && <Check aria-hidden />}
                      </Button>
                    </li>
                  );
                })}
              {!skills.length && (
                <li>
                  No skills yet. Create one in the library to get started.
                </li>
              )}
            </ul>
          )}
          {error && (
            <div>
              <p role="alert">{error}</p>
              <Button variant="outline" onClick={() => void load()}>
                Reload chat and skills
              </Button>
            </div>
          )}
          <DialogFooter>
            <Button variant="ghost" asChild>
              <Link href="/skills">Open library</Link>
            </Button>
            <Button
              variant="outline"
              disabled={saving}
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button
              disabled={
                loading ||
                saving ||
                disabled ||
                selected.some((id) => {
                  const s = skills.find((s) => s.id === id);
                  return (
                    !s ||
                    !s.enabled ||
                    s.deleted ||
                    !(
                      source === "all" ||
                      s.source === "all" ||
                      s.source === source
                    )
                  );
                })
              }
              onClick={() => void save(selected)}
            >
              {saving ? "Saving…" : "Apply to chat"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
