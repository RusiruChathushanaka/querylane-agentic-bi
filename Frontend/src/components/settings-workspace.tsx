"use client";

import Link from "next/link";
import { useState } from "react";
import { useTheme } from "next-themes";
import {
  ArrowLeft,
  ArrowUpRight,
  AudioLines,
  BarChart3,
  Check,
  CheckCheck,
  Globe2,
  MessageSquare,
  Monitor,
  Moon,
  Palette,
  RotateCcw,
  Settings2,
  ShieldCheck,
  Sun,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldTitle,
} from "@/components/ui/field";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  useHydrated,
  usePreferences,
  updatePreference,
  resetPreferences,
} from "@/hooks/use-preferences";
import { ACCENTS, type Preferences } from "@/lib/preferences";

const sections = [
  { id: "appearance", label: "Appearance", icon: Palette, number: "01" },
  { id: "analysis", label: "Analysis & charts", icon: BarChart3, number: "02" },
  {
    id: "conversation",
    label: "Conversation",
    icon: MessageSquare,
    number: "03",
  },
  { id: "voice", label: "Voice", icon: AudioLines, number: "04" },
];

function SwitchSetting({
  id,
  label,
  description,
  value,
  onChange,
}: {
  id: string;
  label: string;
  description: string;
  value: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <Field orientation="horizontal" className="settings-row">
      <FieldContent>
        <FieldLabel htmlFor={id}>{label}</FieldLabel>
        <FieldDescription id={`${id}-hint`}>{description}</FieldDescription>
      </FieldContent>
      <Switch
        id={id}
        checked={value}
        onCheckedChange={onChange}
        aria-describedby={`${id}-hint`}
      />
    </Field>
  );
}

function ChoiceSetting<K extends keyof Preferences>({
  id,
  label,
  description,
  value,
  options,
}: {
  id: K;
  label: string;
  description: string;
  value: string;
  options: readonly (readonly [string, string])[];
}) {
  return (
    <Field orientation="horizontal" className="settings-row">
      <FieldContent>
        <FieldLabel htmlFor={id}>{label}</FieldLabel>
        <FieldDescription id={`${id}-hint`}>{description}</FieldDescription>
      </FieldContent>
      <Select
        value={value}
        onValueChange={(next) => updatePreference(id, next as Preferences[K])}
      >
        <SelectTrigger
          id={id}
          aria-describedby={`${id}-hint`}
          className="settings-select"
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            {options.map(([key, text]) => (
              <SelectItem key={key} value={key}>
                {text}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
    </Field>
  );
}

function ThemePreview({ decimals }: { decimals: string }) {
  return (
    <div
      className="theme-preview"
      role="group"
      aria-label="Live appearance preview with sample retail data"
    >
      <div className="preview-toolbar">
        <span className="preview-dot" />
        <span>YOUR NEXT DISCOVERY</span>
        <Badge variant="secondary">Live preview</Badge>
      </div>
      <div className="preview-body">
        <div className="preview-metric">
          <span>Retail revenue</span>
          <strong>
            {new Intl.NumberFormat("en-US", {
              style: "currency",
              currency: "USD",
              minimumFractionDigits: Number(decimals),
              maximumFractionDigits: Number(decimals),
            }).format(82450.6)}
          </strong>
          <span className="preview-trend">
            <ArrowUpRight aria-hidden /> 12.8% vs. last month
          </span>
        </div>
        <div className="preview-bars" aria-hidden="true">
          {[42, 64, 51, 80, 67, 96, 85].map((height, index) => (
            <div key={index}>
              <span style={{ height: `${height}%` }} />
              <small>{["M", "T", "W", "T", "F", "S", "S"][index]}</small>
            </div>
          ))}
        </div>
      </div>
      <div className="preview-caption">
        <ShieldCheck aria-hidden /> A little more clarity. A little more you.
        <span>Sample data</span>
      </div>
    </div>
  );
}

export function SettingsWorkspace() {
  const { preferences: p, persistent } = usePreferences();
  const hydrated = useHydrated();
  const { theme, setTheme, systemTheme } = useTheme();
  const [resetOpen, setResetOpen] = useState(false);
  const [active, setActive] = useState("appearance");

  function reset() {
    resetPreferences();
    setTheme("system");
    setResetOpen(false);
    toast.success("Preferences restored to defaults");
  }

  return (
    <div className="settings-shell">
      <a className="skip-link" href="#settings-main">
        Skip to settings
      </a>
      <aside className="settings-sidebar">
        <Link href="/" className="settings-brand">
          <span className="settings-brand-mark">
            <BarChart3 aria-hidden />
          </span>
          Querylane<span className="brand-period">.</span>
        </Link>
        <Button asChild variant="outline" className="settings-back">
          <Link href="/">
            <ArrowLeft data-icon="inline-start" /> Back to workspace
          </Link>
        </Button>
        <div className="sidebar-label">YOUR PREFERENCES</div>
        <nav aria-label="Settings sections" className="settings-nav">
          {sections.map(({ id, label, icon: Icon, number }) => (
            <a
              key={id}
              href={`#${id}`}
              aria-current={active === id ? "location" : undefined}
              onClick={() => setActive(id)}
            >
              <Icon aria-hidden />
              <span>{label}</span>
              <small>{number}</small>
            </a>
          ))}
        </nav>
        <div className="settings-local-note">
          <Monitor aria-hidden />
          <strong>Made for this browser</strong>
          <p>
            Your preferences stay on this device. Shared conversations stay
            public.
          </p>
        </div>
      </aside>
      <div className="settings-main-wrap">
        <header className="settings-topbar">
          <span>
            <Settings2 aria-hidden /> Workspace / <strong>Settings</strong>
          </span>
          <Badge variant="secondary">
            <Globe2 data-icon="inline-start" /> Public demo
          </Badge>
        </header>
        <main id="settings-main" className="settings-main">
          <div className="settings-heading">
            <div>
              <p className="settings-eyebrow">
                A WORKSPACE THAT FEELS LIKE YOU
              </p>
              <h1>
                Settings<span>.</span>
              </h1>
              <p>Set the mood. Shape the way you explore.</p>
            </div>
            <span className="settings-save-state" role="status">
              <CheckCheck aria-hidden />
              {persistent ? "Saved automatically" : "For this visit only"}
            </span>
          </div>
          <div className="settings-mobile-back">
            <Button asChild variant="outline" size="sm">
              <Link href="/">
                <ArrowLeft data-icon="inline-start" /> Workspace
              </Link>
            </Button>
          </div>
          {!persistent && (
            <Alert>
              <Monitor />
              <AlertTitle>Browser storage is unavailable</AlertTitle>
              <AlertDescription>
                Your changes work for this visit. Allow site storage to keep
                them after reloading.
              </AlertDescription>
            </Alert>
          )}
          <section
            id="appearance"
            className="settings-section"
            aria-labelledby="appearance-title"
          >
            <div className="settings-section-heading">
              <span>01</span>
              <div>
                <h2 id="appearance-title">Appearance</h2>
                <p>
                  Find your focus, from the first question to the final chart.
                </p>
              </div>
            </div>
            <Card>
              <CardHeader>
                <CardTitle>Your workspace, in your colors</CardTitle>
                <CardDescription>
                  Changes apply instantly across Querylane.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FieldSet>
                  <FieldLegend className="sr-only">
                    Appearance preferences
                  </FieldLegend>
                  <FieldGroup className="settings-fields">
                    <Field className="settings-theme-field">
                      <FieldTitle id="color-mode-label">Color mode</FieldTitle>
                      <FieldDescription id="color-mode-hint">
                        System follows your device
                        {hydrated
                          ? `, currently ${systemTheme ?? "light"}`
                          : ""}
                        .
                      </FieldDescription>
                      <ToggleGroup
                        type="single"
                        variant="outline"
                        spacing={3}
                        value={hydrated ? (theme ?? "system") : ""}
                        disabled={!hydrated}
                        onValueChange={(value) => {
                          if (value) setTheme(value);
                        }}
                        aria-labelledby="color-mode-label"
                        aria-describedby="color-mode-hint"
                        className="theme-mode-options"
                      >
                        {[
                          { value: "light", label: "Light", icon: Sun },
                          { value: "dark", label: "Dark", icon: Moon },
                          { value: "system", label: "System", icon: Monitor },
                        ].map(({ value, label, icon: Icon }) => (
                          <ToggleGroupItem key={value} value={value}>
                            <span
                              className={`theme-mode-thumbnail theme-thumbnail-${value}`}
                              aria-hidden
                            >
                              <i />
                              <i />
                              <i />
                            </span>
                            <span>
                              <Icon aria-hidden />
                              {label}
                              <Check
                                className="theme-choice-check"
                                aria-hidden
                              />
                            </span>
                          </ToggleGroupItem>
                        ))}
                      </ToggleGroup>
                    </Field>
                    <Field orientation="horizontal" className="settings-row">
                      <FieldContent>
                        <FieldTitle id="accent-label">Accent color</FieldTitle>
                        <FieldDescription>
                          Give buttons, highlights, and charts a different
                          character.
                        </FieldDescription>
                      </FieldContent>
                      <ToggleGroup
                        type="single"
                        spacing={2}
                        value={p.accent}
                        onValueChange={(value) => {
                          if (ACCENTS.includes(value as Preferences["accent"]))
                            updatePreference(
                              "accent",
                              value as Preferences["accent"],
                            );
                        }}
                        aria-labelledby="accent-label"
                        className="accent-options"
                      >
                        {ACCENTS.map((accent) => (
                          <ToggleGroupItem
                            value={accent}
                            key={accent}
                            aria-label={`${accent[0].toUpperCase()}${accent.slice(1)} accent`}
                            className="accent-option"
                          >
                            <span data-swatch={accent}>
                              <Check aria-hidden />
                            </span>
                            <small>
                              {accent[0].toUpperCase()}
                              {accent.slice(1)}
                            </small>
                          </ToggleGroupItem>
                        ))}
                      </ToggleGroup>
                    </Field>
                    <ThemePreview decimals={p.decimals} />
                    <Field orientation="horizontal" className="settings-row">
                      <FieldContent>
                        <FieldTitle id="density-label">
                          Workspace density
                        </FieldTitle>
                        <FieldDescription>
                          Choose how much breathing room your data gets.
                        </FieldDescription>
                      </FieldContent>
                      <ToggleGroup
                        type="single"
                        value={p.density}
                        variant="outline"
                        onValueChange={(value) => {
                          if (value === "comfortable" || value === "compact")
                            updatePreference("density", value);
                        }}
                        aria-labelledby="density-label"
                      >
                        <ToggleGroupItem value="comfortable">
                          Comfortable
                        </ToggleGroupItem>
                        <ToggleGroupItem value="compact">
                          Compact
                        </ToggleGroupItem>
                      </ToggleGroup>
                    </Field>
                    <SwitchSetting
                      id="reduce-motion"
                      label="Reduce motion"
                      description="Keep transitions still. Your device’s reduced-motion preference is always respected."
                      value={p.reduceMotion}
                      onChange={(value) =>
                        updatePreference("reduceMotion", value)
                      }
                    />
                  </FieldGroup>
                </FieldSet>
              </CardContent>
            </Card>
          </section>
          <section
            id="analysis"
            className="settings-section"
            aria-labelledby="analysis-title"
          >
            <div className="settings-section-heading">
              <span>02</span>
              <div>
                <h2 id="analysis-title">Analysis & charts</h2>
                <p>A useful starting point for every exploration.</p>
              </div>
            </div>
            <Card>
              <CardHeader>
                <CardTitle>Start with the right view</CardTitle>
                <CardDescription>
                  Presentation preferences keep the underlying results and
                  evidence intact.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FieldSet>
                  <FieldLegend className="sr-only">
                    Analysis preferences
                  </FieldLegend>
                  <FieldGroup className="settings-fields">
                    <ChoiceSetting
                      id="defaultSource"
                      label="Default data source"
                      description="Used for new conversations. Existing chats keep their selected sources."
                      value={p.defaultSource}
                      options={[
                        ["all", "All sources"],
                        ["bigquery", "BigQuery"],
                        ["postgres", "PostgreSQL"],
                      ]}
                    />
                    <ChoiceSetting
                      id="visualization"
                      label="Preferred visualization"
                      description="Auto follows the answer’s recommendation. Unsupported choices fall back to a suitable view."
                      value={p.visualization}
                      options={[
                        ["auto", "Auto · recommended"],
                        ["table", "Table"],
                        ["bar", "Bar chart"],
                        ["line", "Line chart"],
                      ]}
                    />
                    <ChoiceSetting
                      id="decimals"
                      label="Decimal places"
                      description="Maximum precision for numeric tables, KPI cards, and chart tooltips. Currency remains USD."
                      value={p.decimals}
                      options={[
                        ["0", "0 · 12,345"],
                        ["1", "1 · 12,345.6"],
                        ["2", "2 · 12,345.67"],
                      ]}
                    />
                  </FieldGroup>
                </FieldSet>
              </CardContent>
            </Card>
          </section>
          <section
            id="conversation"
            className="settings-section"
            aria-labelledby="conversation-title"
          >
            <div className="settings-section-heading">
              <span>03</span>
              <div>
                <h2 id="conversation-title">Conversation</h2>
                <p>Keep your questions flowing, your way.</p>
              </div>
            </div>
            <Card>
              <CardHeader>
                <CardTitle>Make room for curiosity</CardTitle>
                <CardDescription>
                  Small choices that make a long exploration feel effortless.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FieldSet>
                  <FieldLegend className="sr-only">
                    Conversation preferences
                  </FieldLegend>
                  <FieldGroup className="settings-fields">
                    <SwitchSetting
                      id="enter-to-send"
                      label="Enter to send"
                      description="When off, Enter adds a new line. Ctrl or ⌘ + Enter always sends."
                      value={p.enterToSend}
                      onChange={(value) =>
                        updatePreference("enterToSend", value)
                      }
                    />
                    <SwitchSetting
                      id="followups"
                      label="Suggested follow-up questions"
                      description="Show question suggestions below answers to help you explore further."
                      value={p.followups}
                      onChange={(value) => updatePreference("followups", value)}
                    />
                    <SwitchSetting
                      id="auto-scroll"
                      label="Follow new answers"
                      description="Automatically scroll to incoming answers and analysis progress."
                      value={p.autoScroll}
                      onChange={(value) =>
                        updatePreference("autoScroll", value)
                      }
                    />
                  </FieldGroup>
                </FieldSet>
              </CardContent>
            </Card>
          </section>
          <section
            id="voice"
            className="settings-section"
            aria-labelledby="voice-title"
          >
            <div className="settings-section-heading">
              <span>04</span>
              <div>
                <h2 id="voice-title">Voice</h2>
                <p>Speak naturally. Stay in control.</p>
              </div>
            </div>
            <Card>
              <CardHeader>
                <CardTitle>Set the tone of your conversation</CardTitle>
                <CardDescription>
                  Voice preferences apply when you start or reconnect a voice
                  session.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FieldSet>
                  <FieldLegend className="sr-only">
                    Voice preferences
                  </FieldLegend>
                  <FieldGroup className="settings-fields">
                    <SwitchSetting
                      id="spoken-responses"
                      label="Spoken responses"
                      description="Play the agent’s voice alongside transcripts and visual results. Turn off for a quieter workspace."
                      value={p.spokenResponses}
                      onChange={(value) =>
                        updatePreference("spokenResponses", value)
                      }
                    />
                    <SwitchSetting
                      id="start-muted"
                      label="Start with microphone muted"
                      description="Join voice with your mic off, then unmute when you’re ready to ask."
                      value={p.startMuted}
                      onChange={(value) =>
                        updatePreference("startMuted", value)
                      }
                    />
                  </FieldGroup>
                </FieldSet>
                <div className="settings-voice-note">
                  <ShieldCheck aria-hidden />
                  <p>
                    Microphone access is requested only when you start voice.
                    Transcripts are public; raw audio is not recorded.
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>
          <footer className="settings-reset">
            <div>
              <h2>A fresh start for your preferences</h2>
              <p>
                Restore the defaults on this browser. Shared conversations and
                data stay as they are.
              </p>
            </div>
            <Dialog open={resetOpen} onOpenChange={setResetOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <RotateCcw data-icon="inline-start" />
                  Reset preferences
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Restore default preferences?</DialogTitle>
                  <DialogDescription>
                    This resets appearance, charts, chat, and voice preferences
                    on this browser. It does not delete conversations, results,
                    or your guest session.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="outline">Keep my preferences</Button>
                  </DialogClose>
                  <Button onClick={reset}>Restore defaults</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </footer>
          <p className="settings-bottom-note">
            <Globe2 aria-hidden /> Personal preferences. A shared space for
            discovery.
          </p>
        </main>
      </div>
    </div>
  );
}
