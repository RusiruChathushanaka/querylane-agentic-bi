"use client";

import Link from "next/link";
import { useState } from "react";
import { useTheme } from "next-themes";
import { LayoutGroup, motion } from "motion/react";
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
  updatePreference as persistPreference,
  resetPreferences,
} from "@/hooks/use-preferences";
import { ACCENTS, type Preferences } from "@/lib/preferences";
import {
  ColorSelector,
  ColorSelectorItem,
  ColorSelectorList,
} from "@/components/motion/color-selector";
import { AnimatedNumber } from "@/components/motion/animated-number";
import { useAppMotion } from "@/hooks/use-app-motion";
import { SPRING_LAYOUT } from "@/lib/ease";
import { ModelSettings } from "@/components/model-settings";

const preferenceLabels: Record<keyof Preferences, string> = {
  textModel: "AI model",
  accent: "Accent color",
  density: "Workspace density",
  reduceMotion: "Motion preference",
  defaultSource: "Default data source",
  visualization: "Preferred visualization",
  decimals: "Number formatting",
  chartHighlights: "Automatic chart highlights",
  chartComparisons: "Chart comparisons",
  followups: "Follow-up suggestions",
  autoScroll: "Scrolling preference",
  enterToSend: "Composer shortcut",
  spokenResponses: "Spoken responses",
  startMuted: "Microphone preference",
};

function updatePreference<K extends keyof Preferences>(
  key: K,
  value: Preferences[K],
) {
  const saved = persistPreference(key, value);
  const options = {
    id: "settings-preference",
    description: saved
      ? `${preferenceLabels[key]} updated for this browser.`
      : "Allow browser storage to keep your preferences after reloading.",
    duration: 2600,
  };
  if (saved) toast.success("Preferences saved", options);
  else toast.info("Applied for this visit", options);
}

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
            <AnimatedNumber
              value={82450.6}
              format={(value) =>
                new Intl.NumberFormat("en-US", {
                  style: "currency",
                  currency: "USD",
                  minimumFractionDigits: Number(decimals),
                  maximumFractionDigits: Number(decimals),
                }).format(value)
              }
            />
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
  const { reduced } = useAppMotion();

  function reset() {
    const saved = resetPreferences();
    setTheme("system");
    setResetOpen(false);
    toast.success("Preferences restored to defaults", {
      id: "settings-preference",
      description: saved
        ? "Shared conversations and results are unchanged."
        : "Defaults apply for this visit. Browser storage is unavailable.",
    });
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
        <Button asChild variant="ghost">
          <Link href="/skills">Skills library</Link>
        </Button>
        <LayoutGroup id="settings-navigation">
          <nav aria-label="Settings sections" className="settings-nav">
            {sections.map(({ id, label, icon: Icon, number }) => (
              <a
                key={id}
                href={`#${id}`}
                aria-current={active === id ? "location" : undefined}
                onClick={() => setActive(id)}
              >
                {active === id && (
                  <motion.span
                    className="settings-nav-indicator"
                    layoutId={reduced ? undefined : "active-section"}
                    transition={SPRING_LAYOUT}
                    aria-hidden
                  />
                )}
                <Icon aria-hidden />
                <span>{label}</span>
                <small>{number}</small>
              </a>
            ))}
          </nav>
        </LayoutGroup>
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
        <motion.main
          id="settings-main"
          className="settings-main"
          initial={hydrated && !reduced ? { opacity: 0, y: 8 } : false}
          animate={{ opacity: 1, y: 0 }}
        >
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
                          if (value) {
                            setTheme(value);
                            toast.success("Color mode updated", {
                              id: "settings-preference",
                              description:
                                value === "system"
                                  ? "Your workspace follows the device’s appearance."
                                  : `${value === "dark" ? "Dark" : "Light"} mode is active.`,
                              duration: 2600,
                            });
                          }
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
                      <ColorSelector
                        value={p.accent}
                        onValueChange={(value) => {
                          if (ACCENTS.includes(value as Preferences["accent"]))
                            updatePreference(
                              "accent",
                              value as Preferences["accent"],
                            );
                        }}
                        aria-labelledby="accent-label"
                        className="beui-accent-options"
                      >
                        <ColorSelectorList>
                          {ACCENTS.map((accent) => (
                            <div className="beui-accent-choice" key={accent}>
                              <ColorSelectorItem
                                value={accent}
                                label={`${accent[0].toUpperCase()}${accent.slice(1)} accent`}
                                color={`var(--swatch-${accent})`}
                              />
                              <small aria-hidden="true">
                                {accent[0].toUpperCase()}
                                {accent.slice(1)}
                              </small>
                            </div>
                          ))}
                        </ColorSelectorList>
                      </ColorSelector>
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
                <CardTitle>Choose how you analyze</CardTitle>
                <CardDescription>
                  Choose an AI model and a useful starting view for your
                  results.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FieldSet>
                  <FieldLegend className="sr-only">
                    Analysis preferences
                  </FieldLegend>
                  <FieldGroup className="settings-fields">
                    <ModelSettings
                      value={p.textModel}
                      disabled={!hydrated}
                      onChange={(value) => updatePreference("textModel", value)}
                    />
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
                    <SwitchSetting id="chartHighlights" label="Automatic chart highlights" description="Emphasize peaks and leading values with factual insight chips." value={p.chartHighlights} onChange={(value) => updatePreference("chartHighlights", value)} />
                    <SwitchSetting id="chartComparisons" label="Show chart comparisons" description="Display available target and comparison series by default." value={p.chartComparisons} onChange={(value) => updatePreference("chartComparisons", value)} />
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
        </motion.main>
      </div>
    </div>
  );
}
