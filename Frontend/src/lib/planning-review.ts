import type { ProposedCard } from "./planning-types";

/** Explain the complete saved-evidence change set before explicit publication. */
export function dashboardChanges(
  base: ProposedCard[],
  proposed: ProposedCard[],
) {
  const previous = new Map(
    base.map((card, index) => [card.artifact_id, { card, index }]),
  );
  const next = new Set(proposed.map((card) => card.artifact_id));
  return {
    cards: proposed.map((card, index) => {
      const old = previous.get(card.artifact_id);
      const modified =
        old &&
        (old.index !== index ||
          ["title", "note", "width", "view"].some(
            (field) =>
              JSON.stringify(old.card[field as keyof ProposedCard]) !==
              JSON.stringify(card[field as keyof ProposedCard]),
          ));
      return {
        id: card.artifact_id,
        status: !old ? "Added" : modified ? "Modified" : "Retained",
      };
    }),
    removed: base.filter((card) => !next.has(card.artifact_id)),
  };
}
