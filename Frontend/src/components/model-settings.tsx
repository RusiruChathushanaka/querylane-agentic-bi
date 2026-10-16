"use client";

import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { api } from "@/lib/api";
import { TEXT_MODEL_CHOICES, type Preferences } from "@/lib/preferences";
import { Button } from "@/components/ui/button";
import { Field, FieldDescription, FieldTitle } from "@/components/ui/field";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

type Catalog = {
  models: { id: string; name: string; description: string }[];
  default_model: string;
  mode: "fixture" | "gemini";
  live_model: string;
};

export function ModelSettings({
  value,
  disabled,
  onChange,
}: {
  value: Preferences["textModel"];
  disabled: boolean;
  onChange: (value: Preferences["textModel"]) => void;
}) {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    void api<Catalog>("/models")
      .then((result) => {
        if (active) setCatalog(result);
      })
      .catch(() => {
        if (active)
          setError(
            "Model choices are unavailable. Your saved preference is unchanged.",
          );
      });
    return () => {
      active = false;
    };
  }, [attempt]);

  return (
    <Field>
      <FieldTitle id="text-model-label">AI model</FieldTitle>
      <FieldDescription id="text-model-hint">
        Choose the model for your next question or new voice session’s data
        analysis. Saved for this browser; work already in progress keeps its
        model.
      </FieldDescription>
      {catalog ? (
        <>
          <ToggleGroup
            type="single"
            variant="outline"
            orientation="vertical"
            value={value}
            disabled={disabled}
            aria-labelledby="text-model-label"
            aria-describedby="text-model-hint text-model-scope"
            className="w-full items-stretch"
            onValueChange={(next) => {
              if (TEXT_MODEL_CHOICES.includes(next as Preferences["textModel"]))
                onChange(next as Preferences["textModel"]);
            }}
          >
            <ToggleGroupItem
              value="default"
              className="h-auto min-h-12 justify-between whitespace-normal py-3 text-left"
            >
              <span>
                Workspace default ·{" "}
                {catalog.models.find(
                  (model) => model.id === catalog.default_model,
                )?.name ?? catalog.default_model}
              </span>
              {value === "default" && <Check aria-hidden />}
            </ToggleGroupItem>
            {catalog.models.map((model) => (
              <ToggleGroupItem
                key={model.id}
                value={model.id}
                className="h-auto min-h-12 justify-between whitespace-normal py-3 text-left"
              >
                <span className="flex flex-col gap-1">
                  <span>{model.name}</span>
                  <span className="font-normal">{model.description}</span>
                </span>
                {value === model.id && <Check aria-hidden />}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          <FieldDescription id="text-model-scope">
            Live speech and skill interviews use their dedicated voice model.
            Search embeddings keep their configured model.
          </FieldDescription>
          {catalog.mode === "fixture" && (
            <FieldDescription role="status">
              Local sample mode is active: answers use deterministic sample
              queries, with no model calls. Your selection applies when Gemini
              is enabled.
            </FieldDescription>
          )}
        </>
      ) : error ? (
        <>
          <p role="status">{error}</p>
          <Button
            variant="outline"
            onClick={() => {
              setError("");
              setAttempt((previous) => previous + 1);
            }}
          >
            Retry model choices
          </Button>
        </>
      ) : (
        <p role="status">Loading model choices…</p>
      )}
    </Field>
  );
}
