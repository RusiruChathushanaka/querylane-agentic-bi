"use client";
import { useLayoutEffect } from "react";
import { configureBackend } from "@/lib/api";

export function RuntimeBootstrap({ backendUrl, children }: { backendUrl: string; children: React.ReactNode }) {
  useLayoutEffect(() => { configureBackend(backendUrl); }, [backendUrl]);
  return children;
}
