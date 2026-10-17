import { useMemo, useState } from "react";
import Icon from "../../../components/Icon";
import type { Deck } from "../types";
import DeckCard from "./DeckCard";

type DeckCollectionProps = {
  decks: Deck[];
  loading: boolean;
  error: string;
  onRetry: () => void;
  onCreate: () => void;
  onEdit: (deck: Deck) => void;
  onDelete: (deck: Deck) => void;
};

function LoadingGrid() {
  return (
    <div className="loading-grid" aria-label="Loading decks">
      <div className="loading-card" />
      <div className="loading-card" />
      <div className="loading-card" />
    </div>
  );
}

function EmptyState({
  hasSearch,
  onCreate,
  onClearSearch,
}: {
  hasSearch: boolean;
  onCreate: () => void;
  onClearSearch: () => void;
}) {
  return (
    <div className="empty-state">
      <div className="empty-illustration" aria-hidden="true">
        <span className="empty-card empty-card-back" />
        <span className="empty-card empty-card-front">
          <Icon name="layers" size={26} />
        </span>
        <span className="empty-spark spark-one">✳</span>
        <span className="empty-spark spark-two">✦</span>
      </div>
      <h3>{hasSearch ? "No decks found" : "Your library starts here"}</h3>
      <p>
        {hasSearch
          ? "Try another search, or clear it to see all your decks."
          : "Create your first deck to start collecting the things you want to learn."}
      </p>
      {hasSearch ? (
        <button className="button button-secondary" onClick={onClearSearch}>
          Clear search
        </button>
      ) : (
        <button className="button button-primary" onClick={onCreate}>
          <Icon name="plus" size={18} /> Create your first deck
        </button>
      )}
    </div>
  );
}

function DeckCollection({
  decks,
  loading,
  error,
  onRetry,
  onCreate,
  onEdit,
  onDelete,
}: DeckCollectionProps) {
  const [query, setQuery] = useState("");
  const filteredDecks = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    if (!normalizedQuery) return decks;

    return decks.filter((deck) =>
      `${deck.name} ${deck.description ?? ""}`
        .toLocaleLowerCase()
        .includes(normalizedQuery),
    );
  }, [decks, query]);

  return (
    <section className="deck-section" aria-labelledby="deck-heading">
      <div className="section-heading-row">
        <div>
          <div className="section-kicker">COLLECTIONS</div>
          <h2 id="deck-heading">
            Your decks <span className="heading-count">{decks.length}</span>
          </h2>
        </div>
        <label className="search-box">
          <Icon name="search" size={18} />
          <input
            type="search"
            placeholder="Find a deck..."
            aria-label="Find a deck"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </div>

      {error && (
        <div className="status-banner" role="alert">
          <div>
            <strong>There was a problem with your library.</strong>
            <span>
              {error} Make sure the backend is running at 127.0.0.1:8000.
            </span>
          </div>
          <button className="button button-subtle" onClick={onRetry}>
            <Icon name="refresh" size={16} /> Try again
          </button>
        </div>
      )}

      {loading ? (
        <LoadingGrid />
      ) : filteredDecks.length > 0 ? (
        <div className="deck-grid">
          {filteredDecks.map((deck, index) => (
            <DeckCard
              key={deck.id}
              deck={deck}
              index={index}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          hasSearch={Boolean(query)}
          onCreate={onCreate}
          onClearSearch={() => setQuery("")}
        />
      )}
    </section>
  );
}

export default DeckCollection;
