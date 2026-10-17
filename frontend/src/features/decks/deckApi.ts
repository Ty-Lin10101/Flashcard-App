import type {
  ApiMessage,
  Deck,
  DeckFormValues,
  DeckPayload,
} from "./types";

const API_URL = "http://127.0.0.1:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export function getDecks(): Promise<Deck[]> {
  return request<Deck[]>("/decks");
}

export async function createDeck(deck: DeckPayload): Promise<void> {
  const result = await request<ApiMessage>("/decks", {
    method: "POST",
    body: JSON.stringify({
      ...deck,
      description: deck.description || null,
    }),
  });

  if (result.error) {
    throw new Error(result.error);
  }
}

export function updateDeck(
  deckId: number,
  deck: DeckFormValues,
): Promise<ApiMessage> {
  return request<ApiMessage>(`/decks/${deckId}`, {
    method: "PATCH",
    body: JSON.stringify({
      name: deck.name,
      description: deck.description || null,
    }),
  });
}

export function deleteDeck(deckId: number): Promise<ApiMessage> {
  return request<ApiMessage>(`/decks/${deckId}`, {
    method: "DELETE",
  });
}
