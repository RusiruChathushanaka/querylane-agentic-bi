"use client";

import dynamic from "next/dynamic";
import type { ComponentProps } from "react";
import type ResultCardImplementation from "./result-card";
import { ReadyResultCard } from "./saved-card-loader";
import { Skeleton } from "./ui/skeleton";

const DeferredResultCard = dynamic(() => import("./result-card"), {
  loading: () => <Skeleton className="result-loading min-h-80 w-full" />,
});

/** Reuse ready code synchronously, avoiding another Suspense wait after metadata. */
export default function PreparedResultCard(props: ComponentProps<typeof ResultCardImplementation>) {
  return ReadyResultCard ? <ReadyResultCard {...props} /> : <DeferredResultCard {...props} />;
}
