export const PREFERENCES_KEY = "querylane-preferences-v1";
export const THEME_KEY = "querylane-theme";
export const ACCENTS = ["cobalt", "teal", "violet", "rose"] as const;
export const TEXT_MODEL_CHOICES = [
  "default",
  "gemini-3.8-flash",
  "gemini-3.5-flash-lite",
] as const;

export interface Preferences {
  textModel: (typeof TEXT_MODEL_CHOICES)[number];
  accent: (typeof ACCENTS)[number];
  density: "comfortable" | "compact";
  reduceMotion: boolean;
  defaultSource: "all" | "bigquery" | "postgres";
  visualization: "auto" | "table" | "bar" | "line";
  decimals: "0" | "1" | "2";
  chartHighlights: boolean;
  chartComparisons: boolean;
  followups: boolean;
  autoScroll: boolean;
  enterToSend: boolean;
  spokenResponses: boolean;
  startMuted: boolean;
}

export const DEFAULT_PREFERENCES: Readonly<Preferences> = Object.freeze({
  textModel: "default",
  accent: "cobalt",
  density: "comfortable",
  reduceMotion: false,
  defaultSource: "all",
  visualization: "auto",
  decimals: "2",
  chartHighlights: true,
  chartComparisons: true,
  followups: true,
  autoScroll: true,
  enterToSend: true,
  spokenResponses: true,
  startMuted: false,
});

const choices = {
  textModel: TEXT_MODEL_CHOICES,
  accent: ACCENTS,
  density: ["comfortable", "compact"],
  defaultSource: ["all", "bigquery", "postgres"],
  visualization: ["auto", "table", "bar", "line"],
  decimals: ["0", "1", "2"],
};

// Only allow known keys and values, including when storage is edited externally.
export function parsePreferences(raw: string | null): Preferences {
  const result = { ...DEFAULT_PREFERENCES };
  try {
    const input: unknown = JSON.parse(raw ?? "null");
    if (!input || typeof input !== "object" || Array.isArray(input))
      return result;
    for (const key of Object.keys(result) as (keyof Preferences)[]) {
      const value = (input as Record<string, unknown>)[key];
      const allowed = choices[key as keyof typeof choices] as
        | readonly unknown[]
        | undefined;
      if (allowed ? allowed.includes(value) : typeof value === "boolean")
        Object.assign(result, { [key]: value });
    }
  } catch {
    /* Corrupt or older storage falls back to defaults. */
  }
  return result;
}

// Runs before paint; values written to the DOM are validated rather than interpolated.
export const appearanceScript = `(()=>{try{const p=JSON.parse(localStorage.getItem(${JSON.stringify(PREFERENCES_KEY)})||'{}')||{};const d=document.documentElement;d.dataset.accent=${JSON.stringify(ACCENTS)}.includes(p.accent)?p.accent:'cobalt';d.dataset.density=p.density==='compact'?'compact':'comfortable';d.dataset.reduceMotion=p.reduceMotion===true?'true':'false'}catch{}})()`;
