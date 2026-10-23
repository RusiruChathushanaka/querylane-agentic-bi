import NextLink from "next/link";
import type { ComponentProps } from "react";

/** Application reads take priority over unrequested routes. Click navigation stays client-side. */
export default function AppLink(props: ComponentProps<typeof NextLink>) {
  return <NextLink {...props} prefetch={false} />;
}
