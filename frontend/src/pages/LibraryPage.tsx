import { useState } from "react";
import Icon from "../components/Icon";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import DeckCollection from "../features/decks/components/DeckCollection";
import DeckFormDialog from "../features/decks/components/DeckFormDialog";
import type { Deck, DeckFormValues } from "../features/decks/types";
import { useDeckLibrary } from "../features/decks/useDeckLibrary";
import LibraryOverview from "./LibraryOverview";

function LibraryPage() {
  const {
    decks,
    loading,
    error,
    loadDecks,
    saveDeck,
    removeDeck,
  } = useDeckLibrary();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDeck, setEditingDeck] = useState<Deck | null>(null);
  const scheduledDeckCount = decks.filter(
    (deck) => deck.use_review_dates,
  ).length;

  function openCreateDialog() {
    setEditingDeck(null);
    setDialogOpen(true);
  }

  function openEditDialog(deck: Deck) {
    setEditingDeck(deck);
    setDialogOpen(true);
  }

  async function handleSave(values: DeckFormValues, deck: Deck | null) {
    await saveDeck(values, deck ?? undefined);
    setDialogOpen(false);
    setEditingDeck(null);
  }

  function handleDelete(deck: Deck) {
    const confirmed = window.confirm(
      `Delete “${deck.name}”? This also permanently deletes its cards.`,
    );
    if (confirmed) void removeDeck(deck);
  }

  return (
    <div className="app-shell">
      <Sidebar deckCount={decks.length} />
      <main className="main-content" id="library">
        <Topbar />
        <div className="page-content">
          <section className="welcome-row">
            <div>
              <p className="eyebrow">YOUR PERSONAL KNOWLEDGE BASE</p>
              <h1>A library for <span>curious minds.</span></h1>
              <p className="welcome-copy">
                Keep the things you want to remember, all in one place.
              </p>
            </div>
            <button
              className="button button-primary create-button"
              onClick={openCreateDialog}
            >
              <Icon name="plus" size={19} />
              <span>Create a deck</span>
            </button>
          </section>

          <LibraryOverview
            deckCount={decks.length}
            scheduledDeckCount={scheduledDeckCount}
            loading={loading}
            onCreateDeck={openCreateDialog}
          />

          <DeckCollection
            decks={decks}
            loading={loading}
            error={error}
            onRetry={() => void loadDecks()}
            onCreate={openCreateDialog}
            onEdit={openEditDialog}
            onDelete={handleDelete}
          />

          <footer className="page-footer">
            <span>Made for the things you don’t want to forget.</span>
            <span>One card at a time <span className="footer-star">✳</span></span>
          </footer>
        </div>
      </main>

      {dialogOpen && (
        <DeckFormDialog
          key={editingDeck?.id ?? "new"}
          deck={editingDeck}
          onClose={() => setDialogOpen(false)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

export default LibraryPage;
