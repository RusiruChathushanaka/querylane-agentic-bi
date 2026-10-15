"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowUpRight,
  BookOpen,
  Download,
  FileUp,
  Globe2,
  History,
  LoaderCircle,
  Plus,
  Power,
  RotateCcw,
  Settings2,
  Sparkles,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import { api, ApiError, backendUrl } from "@/lib/api";
import type { Skill, SkillContent, SkillSummary } from "@/lib/types";
import { Reveal } from "@/components/motion/reveal";
import { SkillMarkdown } from "@/components/skill-markdown";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Field,
  FieldGroup,
  FieldLabel,
  FieldDescription,
} from "@/components/ui/field";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

const template: SkillContent = {
  name: "",
  description: "",
  when_to_use: "",
  source: "all",
  tags: [],
  instructions:
    "## Purpose\nDescribe the analytical task this skill helps with.\n\n## Workflow\n1. Check the question and available schema.\n2. Apply the business definitions below.\n3. Explain the result and its assumptions.\n\n## Business definitions\nDocument metric definitions, filters, units, and grain.\n\n## Examples\nAdd example questions or read-only SQL patterns.\n",
};
const contentOf = (skill: Skill): SkillContent =>
  Object.fromEntries(
    Object.keys(template).map((key) => [key, skill[key as keyof SkillContent]]),
  ) as SkillContent;
const sourceLabel = (value: string) =>
  value === "all"
    ? "All sources"
    : value === "postgres"
      ? "PostgreSQL"
      : "BigQuery";

export function SkillsWorkspace() {
  const [skills, setSkills] = useState<SkillSummary[]>([]);
  const [deleted, setDeleted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [source, setSource] = useState("all");
  const [editor, setEditor] = useState<{
    skill?: Skill;
    initial: SkillContent;
  } | null>(null);
  const [draft, setDraft] = useState<SkillContent>(template);
  const [saving, setSaving] = useState(false);
  const [editorError, setEditorError] = useState("");
  const [conflict, setConflict] = useState(false);
  const [discard, setDiscard] = useState(false);
  const [removing, setRemoving] = useState<SkillSummary | null>(null);
  const [pending, setPending] = useState<string | null>(null);
  const [history, setHistory] = useState<{
    skill: SkillSummary;
    revisions?: SkillSummary[];
    error?: string;
  } | null>(null);
  const file = useRef<HTMLInputElement>(null);
  const dirty = Boolean(
    editor && JSON.stringify(draft) !== JSON.stringify(editor.initial),
  );
  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setSkills(
        (await api<{ skills: SkillSummary[] }>(`/skills?deleted=${deleted}`))
          .skills,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "The skills library is unavailable.",
      );
    } finally {
      setLoading(false);
    }
  }, [deleted]);
  useEffect(() => {
    void refresh();
  }, [refresh]);
  useEffect(() => {
    if (!dirty) return;
    const prevent = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", prevent);
    return () => window.removeEventListener("beforeunload", prevent);
  }, [dirty]);

  function openEditor(content: SkillContent, skill?: Skill) {
    setDraft(content);
    setEditor({ skill, initial: content });
    setEditorError("");
    setConflict(false);
  }
  async function editSkill(summary: SkillSummary) {
    setPending(summary.id);
    try {
      const skill = await api<Skill>(`/skills/${summary.id}`);
      if (skill.deleted)
        throw new Error(
          "This skill was deleted. Refresh the library to see its current status.",
        );
      openEditor(contentOf(skill), skill);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Could not open this skill.",
      );
    } finally {
      setPending(null);
    }
  }
  function closeEditor() {
    if (saving) return;
    if (dirty) setDiscard(true);
    else setEditor(null);
  }
  async function save(event: FormEvent) {
    event.preventDefault();
    if (!editor || saving) return;
    if (
      ![
        draft.name,
        draft.description,
        draft.when_to_use,
        draft.instructions,
      ].every((value) => value.trim())
    ) {
      setEditorError(
        "Name, description, when to use, and instructions cannot be blank.",
      );
      return;
    }
    if (
      draft.tags.length > 8 ||
      draft.tags.some(
        (tag) => !tag.trim() || Array.from(tag.trim()).length > 30,
      )
    ) {
      setEditorError(
        "Use up to 8 comma-separated tags, each containing 1–30 characters.",
      );
      return;
    }
    if (new TextEncoder().encode(draft.instructions).length > 16384) {
      setEditorError("Instructions must fit within 16 KiB of UTF-8 text.");
      return;
    }
    setSaving(true);
    setEditorError("");
    try {
      await api<Skill>(
        editor.skill ? `/skills/${editor.skill.id}` : "/skills",
        {
          method: editor.skill ? "PATCH" : "POST",
          body: JSON.stringify({
            ...draft,
            ...(editor.skill
              ? { expected_revision: editor.skill.revision }
              : {}),
          }),
        },
      );
      toast.success(editor.skill ? "Skill updated" : "Skill saved", {
        description:
          editor.skill?.enabled === false
            ? "This skill remains disabled."
            : "The agent can now discover this shared skill.",
      });
      setEditor(null);
      await refresh();
    } catch (err) {
      setEditorError(
        err instanceof Error ? err.message : "Could not save this skill.",
      );
      setConflict(
        err instanceof ApiError &&
          err.status === 409 &&
          err.code === "skill_conflict",
      );
    } finally {
      setSaving(false);
    }
  }
  async function change(
    skill: SkillSummary,
    action: "toggle" | "delete" | "restore",
  ) {
    setPending(skill.id);
    try {
      const value = await api<Skill>(
        `/skills/${skill.id}${action === "delete" ? `?expected_revision=${skill.revision}` : action === "restore" ? "/restore" : ""}`,
        {
          method:
            action === "delete"
              ? "DELETE"
              : action === "restore"
                ? "POST"
                : "PATCH",
          ...(action !== "delete"
            ? {
                body: JSON.stringify({
                  expected_revision: skill.revision,
                  ...(action === "toggle" ? { enabled: !skill.enabled } : {}),
                }),
              }
            : {}),
        },
      );
      if (action === "delete") {
        setRemoving(null);
        toast.success("Skill deleted", {
          description:
            "Saved answers retain this version. You can restore it from Recently deleted.",
          duration: 10000,
          action: {
            label: "Undo",
            onClick: () => {
              void change(value, "restore");
            },
          },
        });
      } else
        toast.success(
          action === "restore"
            ? "Skill restored"
            : value.enabled
              ? "Skill enabled"
              : "Skill disabled",
        );
      await refresh();
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Could not update this skill.",
      );
    } finally {
      setPending(null);
    }
  }
  async function exportFile(skill: SkillSummary) {
    try {
      const response = await fetch(
        `${await backendUrl()}/api/v1/skills/${skill.id}/export`,
        { cache: "no-store" },
      );
      if (!response.ok) throw new Error("Could not export this skill.");
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "SKILL.md";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      toast.success("SKILL.md exported");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Export failed.");
    }
  }
  async function importFile(selected?: File) {
    if (!selected) return;
    try {
      if (!/\.(md|markdown)$/i.test(selected.name) || selected.size > 24576)
        throw new Error("Choose one Markdown file smaller than 24 KiB.");
      const imported = await api<SkillContent>("/skills/import", {
        method: "POST",
        body: JSON.stringify({ markdown: await selected.text() }),
      });
      openEditor(imported);
      toast.info("Markdown imported for review", {
        description: "Review the fields, then save to publish this skill.",
      });
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Could not import this file.",
      );
    } finally {
      if (file.current) file.current.value = "";
    }
  }
  async function showHistory(skill: SkillSummary) {
    setHistory({ skill });
    try {
      const result = await api<{ revisions: SkillSummary[] }>(
        `/skills/${skill.id}/revisions`,
      );
      setHistory((current) =>
        current?.skill.id === skill.id
          ? { skill, revisions: result.revisions }
          : current,
      );
    } catch (err) {
      setHistory((current) =>
        current?.skill.id === skill.id
          ? {
              skill,
              error:
                err instanceof Error ? err.message : "History is unavailable.",
            }
          : current,
      );
    }
  }
  const filtered = skills.filter(
    (skill) =>
      `${skill.name} ${skill.description} ${skill.tags.join(" ")}`
        .toLowerCase()
        .includes(search.toLowerCase()) &&
      (source === "all" || skill.source === "all" || skill.source === source),
  );

  return (
    <div className="skills-shell">
      <a className="skip-link" href="#skills-main">
        Skip to skills library
      </a>
      <header className="skills-header">
        <Link href="/" className="skills-brand">
          <BookOpen aria-hidden /> Querylane<span>.</span>
        </Link>
        <nav aria-label="Workspace">
          <Button variant="ghost" asChild>
            <Link href="/">
              <ArrowLeft aria-hidden /> Workspace
            </Link>
          </Button>
          <Button variant="ghost" asChild>
            <Link href="/settings">
              <Settings2 aria-hidden /> Settings
            </Link>
          </Button>
        </nav>
      </header>
      <main className="skills-main" id="skills-main" tabIndex={-1}>
        <Reveal className="skills-heading">
          <div>
            <p className="welcome-eyebrow">KNOWLEDGE THAT GOES FURTHER</p>
            <h1>
              Skills library<span>.</span>
            </h1>
            <p className="skills-intro">
              Teach your analyst how your business thinks.
              <br />
              Save reusable playbooks for more consistent answers.
            </p>
          </div>
          <div className="skills-heading-actions">
            <input
              ref={file}
              type="file"
              accept=".md,.markdown,text/markdown"
              className="sr-only"
              tabIndex={-1}
              aria-label="Import Markdown file"
              onChange={(event) => void importFile(event.target.files?.[0])}
            />
            <Button variant="outline" onClick={() => file.current?.click()}>
              <FileUp aria-hidden /> Import SKILL.md
            </Button>
            <Button onClick={() => openEditor({ ...template, tags: [] })}>
              <Plus aria-hidden /> Create skill
            </Button>
          </div>
        </Reveal>
        <div className="skills-public-note">
          <Globe2 aria-hidden />
          <p>
            <strong>A shared library, open to everyone.</strong> Any visitor can
            add, edit, or delete skills. Saving publishes immediately. Do not
            include credentials or private information.
          </p>
        </div>
        <div className="skills-toolbar">
          <ToggleGroup
            type="single"
            variant="outline"
            size="sm"
            spacing={0}
            aria-label="Skills view"
            value={deleted ? "deleted" : "active"}
            onValueChange={(value) => {
              if (value) setDeleted(value === "deleted");
            }}
          >
            <ToggleGroupItem value="active">Library</ToggleGroupItem>
            <ToggleGroupItem value="deleted">Recently deleted</ToggleGroupItem>
          </ToggleGroup>
          <div className="skills-filters">
            <Input
              aria-label="Search skills"
              placeholder="Search names, descriptions, tags…"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
            <Select value={source} onValueChange={setSource}>
              <SelectTrigger aria-label="Filter skills by source">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All sources</SelectItem>
                <SelectItem value="bigquery">BigQuery</SelectItem>
                <SelectItem value="postgres">PostgreSQL</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Refresh skills"
              onClick={() => void refresh()}
            >
              <RotateCcw aria-hidden />
            </Button>
          </div>
        </div>
        {error ? (
          <div className="skills-empty">
            <h2>Library unavailable</h2>
            <p role="alert">{error}</p>
            <Button onClick={() => void refresh()}>Try again</Button>
          </div>
        ) : loading ? (
          <div className="skills-grid" aria-label="Loading skills">
            {[0, 1, 2].map((key) => (
              <Skeleton key={key} className="h-64 rounded-xl" />
            ))}
          </div>
        ) : !filtered.length ? (
          <Reveal className="skills-empty">
            <BookOpen aria-hidden />
            <h2>
              {search || source !== "all"
                ? "No matching skills"
                : deleted
                  ? "Nothing in recently deleted"
                  : "Your analyst’s next skill starts here"}
            </h2>
            <p>
              {deleted
                ? "Deleted skills stay recoverable, and saved answers keep their evidence."
                : "Create a playbook for a business metric, a reporting workflow, or a useful analytical habit."}
            </p>
            {!deleted && (
              <Button onClick={() => openEditor({ ...template, tags: [] })}>
                <Plus aria-hidden /> Create your first skill
              </Button>
            )}
          </Reveal>
        ) : (
          <ul
            className="skills-grid"
            aria-label={deleted ? "Deleted skills" : "Shared skills"}
          >
            {filtered.map((skill, index) => (
              <li key={skill.id}>
                <Reveal delay={Math.min(index, 5) * 0.035}>
                  <Card className="skill-card">
                    <CardHeader>
                      <div className="skill-card-status">
                        <span className="skill-card-icon">
                          <BookOpen aria-hidden />
                        </span>
                        <Badge
                          variant={
                            skill.enabled && !deleted ? "secondary" : "outline"
                          }
                        >
                          {deleted
                            ? "Deleted"
                            : skill.enabled
                              ? "Enabled"
                              : "Disabled"}
                        </Badge>
                      </div>
                      <CardTitle>
                        <h2>{skill.name}</h2>
                      </CardTitle>
                      <CardDescription>{skill.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="skill-card-tags">
                        <Badge variant="outline">
                          {sourceLabel(skill.source)}
                        </Badge>
                        {skill.tags.map((tag) => (
                          <Badge variant="outline" key={tag}>
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <p className="skill-card-when">{skill.when_to_use}</p>
                      <p className="skill-card-date">
                        v{skill.revision} · Updated{" "}
                        {new Date(skill.updated_at).toLocaleDateString()}
                      </p>
                    </CardContent>
                    <CardFooter className="skill-card-actions">
                      {deleted ? (
                        <Button
                          variant="outline"
                          disabled={pending === skill.id}
                          onClick={() => void change(skill, "restore")}
                          aria-label={`Restore ${skill.name}`}
                        >
                          <RotateCcw aria-hidden /> Restore
                        </Button>
                      ) : (
                        <>
                          <Button
                            variant="outline"
                            disabled={pending === skill.id}
                            onClick={() => void editSkill(skill)}
                            aria-label={`Edit ${skill.name}`}
                          >
                            Edit skill <ArrowUpRight aria-hidden />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            disabled={pending === skill.id}
                            onClick={() => void change(skill, "toggle")}
                            aria-label={`${skill.enabled ? "Disable" : "Enable"} ${skill.name}`}
                          >
                            <Power aria-hidden />
                          </Button>
                        </>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => void showHistory(skill)}
                        aria-label={`Version history of ${skill.name}`}
                      >
                        <History aria-hidden />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => void exportFile(skill)}
                        aria-label={`Export ${skill.name}`}
                      >
                        <Download aria-hidden />
                      </Button>
                      {!deleted && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setRemoving(skill)}
                          aria-label={`Delete ${skill.name}`}
                        >
                          <Trash2 aria-hidden />
                        </Button>
                      )}
                    </CardFooter>
                  </Card>
                </Reveal>
              </li>
            ))}
          </ul>
        )}
        <p className="skills-footnote">
          <Sparkles aria-hidden /> Relevant skills are discovered automatically.
          Attach up to three to any exploration.
        </p>
      </main>
      <Dialog
        open={Boolean(editor)}
        onOpenChange={(open) => {
          if (!open) closeEditor();
        }}
      >
        <DialogContent
          className="skill-editor-dialog"
          onEscapeKeyDown={(event) => {
            if (saving) event.preventDefault();
          }}
        >
          <DialogHeader>
            <DialogTitle>
              {editor?.skill ? "Edit skill" : "Create a skill"}
            </DialogTitle>
            <DialogDescription>
              Public Markdown playbooks guide analytics. Saving publishes
              immediately; scripts and new tools are not supported.
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={(event) => void save(event)}
            className="skill-editor-form"
          >
            <fieldset disabled={saving} className="skill-editor-fields">
              <legend className="sr-only">Skill details</legend>
              <FieldGroup>
                <Field>
                  <FieldLabel htmlFor="skill-name">Name</FieldLabel>
                  <Input
                    id="skill-name"
                    required
                    maxLength={80}
                    value={draft.name}
                    onChange={(event) =>
                      setDraft({ ...draft, name: event.target.value })
                    }
                    placeholder="e.g. Monthly revenue review"
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="skill-description">
                    Description
                  </FieldLabel>
                  <Input
                    id="skill-description"
                    required
                    maxLength={300}
                    value={draft.description}
                    onChange={(event) =>
                      setDraft({ ...draft, description: event.target.value })
                    }
                    placeholder="What does this skill help the analyst do?"
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="skill-when">When to use</FieldLabel>
                  <Textarea
                    id="skill-when"
                    required
                    maxLength={500}
                    rows={2}
                    value={draft.when_to_use}
                    onChange={(event) =>
                      setDraft({ ...draft, when_to_use: event.target.value })
                    }
                    placeholder="Use when a question asks about…"
                  />
                </Field>
                <div className="skill-editor-pair">
                  <Field>
                    <FieldLabel htmlFor="skill-source">
                      Source compatibility
                    </FieldLabel>
                    <Select
                      value={draft.source}
                      onValueChange={(value) =>
                        setDraft({
                          ...draft,
                          source: value as SkillContent["source"],
                        })
                      }
                    >
                      <SelectTrigger id="skill-source">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All sources</SelectItem>
                        <SelectItem value="bigquery">BigQuery</SelectItem>
                        <SelectItem value="postgres">PostgreSQL</SelectItem>
                      </SelectContent>
                    </Select>
                  </Field>
                  <Field>
                    <FieldLabel htmlFor="skill-tags">Tags</FieldLabel>
                    <Input
                      id="skill-tags"
                      value={draft.tags.join(",")}
                      onChange={(event) =>
                        setDraft({
                          ...draft,
                          tags: event.target.value
                            ? event.target.value.split(",")
                            : [],
                        })
                      }
                      placeholder="revenue, reporting"
                      aria-describedby="skill-tags-hint"
                    />
                    <FieldDescription id="skill-tags-hint">
                      Comma-separated, up to 8 tags.
                    </FieldDescription>
                  </Field>
                </div>
                <Tabs defaultValue="instructions">
                  <TabsList aria-label="Skill content">
                    <TabsTrigger value="instructions">Instructions</TabsTrigger>
                    <TabsTrigger value="preview">Preview</TabsTrigger>
                  </TabsList>
                  <TabsContent value="instructions">
                    <Field>
                      <FieldLabel htmlFor="skill-instructions">
                        Markdown instructions
                      </FieldLabel>
                      <FieldDescription id="skill-content-hint">
                        Up to 16 KiB. Define metrics, steps, and examples.
                        Application query safeguards always apply.
                      </FieldDescription>
                      <Textarea
                        id="skill-instructions"
                        aria-describedby="skill-content-hint"
                        className="skill-instructions-input"
                        required
                        rows={12}
                        value={draft.instructions}
                        onChange={(event) =>
                          setDraft({
                            ...draft,
                            instructions: event.target.value,
                          })
                        }
                      />
                    </Field>
                  </TabsContent>
                  <TabsContent value="preview">
                    <div className="skill-preview">
                      <SkillMarkdown>
                        {draft.instructions || "Nothing to preview yet."}
                      </SkillMarkdown>
                    </div>
                  </TabsContent>
                </Tabs>
              </FieldGroup>
            </fieldset>
            {editorError && (
              <div className="skill-editor-error">
                <p role="alert">{editorError}</p>
                {conflict && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={async () => {
                      if (
                        !editor?.skill ||
                        !window.confirm(
                          "Replace your unsaved draft with the latest saved version?",
                        )
                      )
                        return;
                      try {
                        const latest = await api<Skill>(
                          `/skills/${editor.skill.id}`,
                        );
                        if (latest.deleted) {
                          setEditorError(
                            "This skill was deleted. Close the editor and restore it from Recently deleted.",
                          );
                          return;
                        }
                        openEditor(contentOf(latest), latest);
                      } catch (err) {
                        setEditorError(
                          err instanceof Error
                            ? err.message
                            : "Could not reload.",
                        );
                      }
                    }}
                  >
                    Reload latest
                  </Button>
                )}
              </div>
            )}
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={closeEditor}
                disabled={saving}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving && <LoaderCircle className="spin" aria-hidden />}
                {saving ? "Saving…" : "Save skill"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <Dialog open={discard} onOpenChange={setDiscard}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Discard unsaved changes?</DialogTitle>
            <DialogDescription>
              Your changes have not been saved to the public library.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDiscard(false)}>
              Keep editing
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                setDiscard(false);
                setEditor(null);
              }}
            >
              Discard changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog
        open={Boolean(removing)}
        onOpenChange={(open) => {
          if (!open && !pending) setRemoving(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete {removing?.name}?</DialogTitle>
            <DialogDescription>
              The agent will stop discovering this skill. Existing answers
              retain their saved versions. Restore it later from Recently
              deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              disabled={Boolean(pending)}
              onClick={() => setRemoving(null)}
            >
              Keep skill
            </Button>
            <Button
              variant="destructive"
              disabled={Boolean(pending)}
              onClick={() => {
                if (removing) void change(removing, "delete");
              }}
            >
              Delete skill
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <Dialog
        open={Boolean(history)}
        onOpenChange={(open) => {
          if (!open) setHistory(null);
        }}
      >
        <DialogContent className="skill-history-dialog">
          <DialogHeader>
            <DialogTitle>Version history</DialogTitle>
            <DialogDescription>
              {history?.skill.name} · Saved versions remain available after
              edits and deletion.
            </DialogDescription>
          </DialogHeader>
          {history?.error ? (
            <p role="alert">{history.error}</p>
          ) : !history?.revisions ? (
            <Skeleton className="h-20" />
          ) : (
            <ul className="skill-history-list">
              {history.revisions.map((version) => (
                <li key={version.revision}>
                  <Link
                    href={`/skills/${version.id}/revisions/${version.revision}`}
                  >
                    Version {version.revision}
                    <small>
                      {new Date(version.updated_at).toLocaleString()} ·{" "}
                      {version.deleted
                        ? "Deleted"
                        : version.enabled
                          ? "Enabled"
                          : "Disabled"}
                    </small>
                    <ArrowUpRight aria-hidden />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
