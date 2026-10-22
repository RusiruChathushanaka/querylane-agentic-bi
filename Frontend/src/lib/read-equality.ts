/** Preserve React identity on unchanged JSON reads; no persistent response cache. */
export function retainEqualRead<T>(previous: T, incoming: T): T {
  return JSON.stringify(previous) === JSON.stringify(incoming) ? previous : incoming;
}
