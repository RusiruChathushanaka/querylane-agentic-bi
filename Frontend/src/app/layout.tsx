import type { Metadata } from "next";
import { DM_Sans, IBM_Plex_Mono, Manrope } from "next/font/google";
import { AppProviders } from "@/components/app-providers";
import { appearanceScript } from "@/lib/preferences";
import "./globals.css";
const body = DM_Sans({ variable: "--font-dm-sans", subsets: ["latin"] });
const mono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});
const heading = Manrope({ variable: "--font-manrope", subsets: ["latin"] });
export const metadata: Metadata = {
  title: "Querylane — Retail intelligence, in conversation",
  description:
    "Explore BigQuery and PostgreSQL with questions, live voice, charts, and visible query evidence. Public synthetic retail demo.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${body.variable} ${mono.variable} ${heading.variable}`}
    >
      <head>
        <meta name="color-scheme" content="light dark" />
        <script dangerouslySetInnerHTML={{ __html: appearanceScript }} />
      </head>
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
