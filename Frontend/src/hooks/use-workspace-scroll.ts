"use client";

import { useCallback, useEffect, useRef, useState, type UIEvent } from "react";

/** Only the conversation owns chat scrolling; never scroll the document or portals. */
export function useWorkspaceScroll(autoScroll: boolean) {
  const shell = useRef<HTMLDivElement>(null);
  const scroller = useRef<HTMLElement>(null);
  const followLatest = useRef(true);
  const observer = useRef<ResizeObserver | null>(null);
  const frame = useRef<number | null>(null);
  const [showJump, setShowJump] = useState(false);
  const jumpToLatest = useCallback((explicit = true) => {
    if (explicit) followLatest.current = true;
    if (frame.current !== null) cancelAnimationFrame(frame.current);
    frame.current = requestAnimationFrame(() => {
      frame.current = null;
      const node = scroller.current;
      if (node && followLatest.current) {
        node.scrollTop = node.scrollHeight;
        setShowJump(false);
      }
    });
  }, []);
  const registerBottom = useCallback((node: HTMLDivElement | null) => {
    observer.current?.disconnect();
    if (!node?.parentElement) return;
    const changed = () => {
      const scroll = scroller.current;
      if (autoScroll && followLatest.current) jumpToLatest(false);
      else if (scroll) setShowJump(scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight > 40);
    };
    changed();
    observer.current = new ResizeObserver(changed);
    observer.current.observe(node.parentElement);
  }, [autoScroll, jumpToLatest]);
  const resetFollowing = useCallback(() => { followLatest.current = true; setShowJump(false); }, []);
  const pauseFollowing = useCallback(() => { followLatest.current = false; }, []);
  const onScroll = useCallback((event: UIEvent<HTMLElement>) => {
    const node = event.currentTarget;
    const nearEnd = node.scrollHeight - node.scrollTop - node.clientHeight < 40;
    followLatest.current = nearEnd;
    setShowJump(!nearEnd);
  }, []);
  useEffect(() => {
    const viewport = window.visualViewport;
    const root = shell.current;
    if (!viewport || !root) return;
    const resize = () => {
      // Leave magnification and panning to the browser when zoomed.
      if (viewport.scale === 1 && window.innerWidth <= 800) {
        root.style.setProperty("--workspace-viewport-height", `${viewport.height}px`);
        root.style.setProperty("--workspace-viewport-offset", `${viewport.offsetTop}px`);
      } else {
        root.style.removeProperty("--workspace-viewport-height");
        root.style.removeProperty("--workspace-viewport-offset");
      }
    };
    resize();
    viewport.addEventListener("resize", resize);
    viewport.addEventListener("scroll", resize);
    window.addEventListener("resize", resize);
    return () => {
      viewport.removeEventListener("resize", resize);
      viewport.removeEventListener("scroll", resize);
      window.removeEventListener("resize", resize);
      root.style.removeProperty("--workspace-viewport-height");
      root.style.removeProperty("--workspace-viewport-offset");
    };
  }, []);
  useEffect(() => () => {
    observer.current?.disconnect();
    if (frame.current !== null) cancelAnimationFrame(frame.current);
  }, []);
  return { shell, scroller, registerBottom, resetFollowing, jumpToLatest, showJump, onScroll, pauseFollowing };
}
