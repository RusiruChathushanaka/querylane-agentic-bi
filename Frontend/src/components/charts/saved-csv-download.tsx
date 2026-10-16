"use client";

import { useState } from "react";
import { Download } from "lucide-react";
import { toast } from "sonner";
import { backendUrl } from "@/lib/api";
import { downloadBlob } from "@/lib/chart-export";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Artifact } from "@/lib/types";

export function SavedCsvDownload({ artifact }: { artifact: Artifact }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  async function download() {
    setBusy(true);
    try {
      const response = await fetch(
        `${await backendUrl()}/api/v1/artifacts/${artifact.id}/export.csv`,
        { cache: "no-store" },
      );
      if (!response.ok)
        throw new Error("The saved result could not be exported. Try again.");
      downloadBlob(
        await response.blob(),
        `querylane-${artifact.id}-${artifact.complete ? "complete" : "partial"}.csv`,
      );
      toast.success("CSV download ready", {
        description: `${artifact.row_count.toLocaleString()} saved rows · ${artifact.complete ? "complete result" : "partial source result"}`,
      });
      setOpen(false);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Export failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
        <Download />
        CSV
      </Button>
      <Dialog
        open={open}
        onOpenChange={(next) => {
          if (!busy) setOpen(next);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Download CSV</DialogTitle>
            <DialogDescription>
              {artifact.row_count.toLocaleString()} saved rows with original
              columns, across every table page.{" "}
              {artifact.complete
                ? "Complete source inputs."
                : "Partial source inputs: this is not a complete population."}
            </DialogDescription>
          </DialogHeader>
          <Button disabled={busy} onClick={() => void download()}>
            {busy ? "Preparing download…" : "Download CSV"}
          </Button>
        </DialogContent>
      </Dialog>
    </>
  );
}
