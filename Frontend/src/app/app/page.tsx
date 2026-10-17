import type { Metadata } from "next";
import Workspace from "@/components/workspace";

export const metadata: Metadata = {
  title: "Workspace | Querylane",
  robots: { index: false, follow: true },
};

export default function WorkspacePage() {
  return <Workspace />;
}
