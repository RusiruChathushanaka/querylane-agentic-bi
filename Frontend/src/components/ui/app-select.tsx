"use client";

import { useState, type ComponentProps, type ReactNode } from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "cn";

// Radix reserves the empty value for clearing. A selectable default/placeholder
// uses a private encoded value; callers keep their original empty-string state.
const EMPTY = "__querylane_empty_choice__";
export const encodeChoice = (value: string | number | undefined) =>
  value === undefined || value === "" ? EMPTY : `v:${value}`;
export const decodeChoice = (value: string) =>
  value === EMPTY ? "" : value.startsWith("v:") ? value.slice(2) : value;

type AppSelectProps = Omit<
  ComponentProps<typeof SelectTrigger>,
  "value" | "defaultValue" | "onChange" | "children"
> & {
  value?: string | number;
  defaultValue?: string | number;
  onValueChange: (value: string) => void;
  children: ReactNode;
  name?: string;
  required?: boolean;
  onCloseAutoFocus?: ComponentProps<typeof SelectContent>["onCloseAutoFocus"];
};

export function AppSelect({
  value,
  defaultValue = "",
  onValueChange,
  children,
  name,
  required,
  disabled,
  className,
  onCloseAutoFocus,
  ...trigger
}: AppSelectProps) {
  const [uncontrolled, setUncontrolled] = useState(String(defaultValue));
  return (
    <Select
      value={encodeChoice(value ?? uncontrolled)}
      onValueChange={(next) => {
        const decoded = decodeChoice(next);
        if (value === undefined) setUncontrolled(decoded);
        onValueChange(decoded);
      }}
      name={name}
      required={required}
      disabled={disabled}
    >
      <SelectTrigger
        {...trigger}
        disabled={disabled}
        className={cn("app-select-trigger w-full min-w-0", className)}
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent onCloseAutoFocus={onCloseAutoFocus}>
        <SelectGroup>{children}</SelectGroup>
      </SelectContent>
    </Select>
  );
}

export function AppSelectItem({
  value,
  ...props
}: Omit<ComponentProps<typeof SelectItem>, "value"> & {
  value: string | number;
}) {
  return <SelectItem value={encodeChoice(value)} {...props} />;
}
