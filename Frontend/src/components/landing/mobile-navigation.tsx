"use client";

import Link from "next/link";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { workspacePath } from "@/lib/workspace-links";

export function LandingMobileNavigation() {
  return (
    <div className="landing-mobile-navigation">
      <Sheet>
        <SheetTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            className="min-h-11 min-w-11"
            aria-label="Open navigation"
          >
            <Menu aria-hidden />
          </Button>
        </SheetTrigger>
        <SheetContent className="landing-sheet">
          <SheetHeader>
            <SheetTitle>Explore Querylane</SheetTitle>
            <SheetDescription>
              Business intelligence, in conversation.
            </SheetDescription>
          </SheetHeader>
          <nav aria-label="Mobile landing navigation">
            {[
              ["Reports", "#reports"],
              ["Predictions", "#predictions"],
              ["Voice BI", "#voice-bi"],
              ["Capabilities", "#capabilities"],
            ].map(([label, href]) => (
              <SheetClose asChild key={href}>
                <a href={href}>{label}</a>
              </SheetClose>
            ))}
            <SheetClose asChild>
              <Link prefetch={false} href={workspacePath()}>
                Open Querylane →
              </Link>
            </SheetClose>
          </nav>
        </SheetContent>
      </Sheet>
    </div>
  );
}
