import { useCallback, useEffect, useState } from "react";
import {
  createDeck as createDeckRequest,
  deleteDeck as deleteDeckRequest,
  getDecks,
  updateDeck as updateDeckRequest,
} from "./deckApi";
import type { Deck, DeckFormValues } from "./types";

export function useDeckLibrary() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDecks = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setDecks(await getDecks());
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Could not connect to the flashcard API.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDecks();
  }, [loadDecks]);

  const saveDeck = useCallback(
    async (deck: DeckFormValues, existingDeck?: Deck) => {
      const payload = {
        name: deck.name.trim(),
        description: deck.description.trim(),
      };

      if (existingDeck) {
        await updateDeckRequest(existingDeck.id, payload);
      } else {
        await createDeckRequest({ ...payload, type: "standard" });
      }

      await loadDecks();
    },
    [loadDecks],
  );

  const removeDeck = useCallback(async (deck: Deck) => {
    try {
      await deleteDeckRequest(deck.id);
      setDecks((currentDecks) =>
        currentDecks.filter((currentDeck) => currentDeck.id !== deck.id),
      );
      setError("");
    } catch (deleteError) {
      setError(
        deleteError instanceof Error
          ? deleteError.message
          : "Could not delete this deck.",
      );
    }
  }, []);

  return {
    decks,
    loading,
    error,
    loadDecks,
    saveDeck,
    removeDeck,
  };
}
