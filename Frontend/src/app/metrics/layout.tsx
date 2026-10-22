import { RuntimeConfig } from "@/components/runtime-config";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <RuntimeConfig>{children}</RuntimeConfig>;
}
