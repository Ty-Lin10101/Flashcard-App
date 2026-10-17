import Icon from "../../../components/Icon";
import type { Deck } from "../types";

type DeckCardProps = {
  deck: Deck;
  index: number;
  onEdit: (deck: Deck) => void;
  onDelete: (deck: Deck) => void;
};

function DeckCard({ deck, index, onEdit, onDelete }: DeckCardProps) {
  return (
    <article className={`deck-card deck-accent-${index % 4}`}>
      <div className="deck-card-top">
        <div className="deck-art" aria-hidden="true">
          <span className="art-back" />
          <span className="art-front">
            <Icon name={index % 2 === 0 ? "book" : "layers"} size={22} />
          </span>
        </div>
        <div className="deck-actions">
          <button
            className="icon-button"
            aria-label={`Edit ${deck.name}`}
            onClick={() => onEdit(deck)}
          >
            <Icon name="edit" size={17} />
          </button>
          <button
            className="icon-button delete-action"
            aria-label={`Delete ${deck.name}`}
            onClick={() => onDelete(deck)}
          >
            <Icon name="trash" size={17} />
          </button>
        </div>
      </div>

      <div className="deck-meta">
        <span className="deck-type">
          <span className="type-dot" /> {deck.type || "Standard"}
        </span>
        {deck.use_review_dates && (
          <span className="review-badge">Spaced repetition</span>
        )}
      </div>
      <h3>{deck.name}</h3>
      <p className="deck-description">
        {deck.description || "A collection of ideas worth remembering."}
      </p>
      <div className="deck-card-footer">
        <span><Icon name="layers" size={15} /> Flashcard deck</span>
        <span className="deck-arrow" aria-hidden="true">
          <Icon name="arrow" size={17} />
        </span>
      </div>
    </article>
  );
}

export default DeckCard;
