import { useState } from "react";
import type { FormEvent } from "react";
import Icon from "../../../components/Icon";
import type { Deck, DeckFormValues } from "../types";

type DeckFormDialogProps = {
  deck: Deck | null;
  onClose: () => void;
  onSave: (values: DeckFormValues, deck: Deck | null) => Promise<void>;
};

function DeckFormDialog({ deck, onClose, onSave }: DeckFormDialogProps) {
  const [values, setValues] = useState<DeckFormValues>({
    name: deck?.name ?? "",
    description: deck?.description ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const name = values.name.trim();
    if (!name) {
      setError("Give your deck a name to continue.");
      return;
    }

    setSaving(true);
    setError("");
    try {
      await onSave(
        { name, description: values.description.trim() },
        deck,
      );
    } catch (saveError) {
      setError(
        saveError instanceof Error ? saveError.message : "Could not save this deck.",
      );
    } finally {
      setSaving(false);
    }
  }

  function closeDialog() {
    if (!saving) onClose();
  }

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) closeDialog();
      }}
    >
      <section
        className="deck-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
      >
        <div className="dialog-header">
          <div className="dialog-mark">
            <Icon name={deck ? "edit" : "layers"} size={21} />
          </div>
          <button
            className="icon-button dialog-close"
            onClick={closeDialog}
            aria-label="Close dialog"
          >
            <Icon name="close" size={19} />
          </button>
        </div>
        <p className="eyebrow">
          {deck ? "UPDATE YOUR COLLECTION" : "START A NEW COLLECTION"}
        </p>
        <h2 id="dialog-title">{deck ? "Edit your deck" : "Create a deck"}</h2>
        <p className="dialog-description">
          {deck
            ? "Give this collection a fresh name or description."
            : "Give your new collection a name. You can add flashcards next."}
        </p>
        <form onSubmit={(event) => void handleSubmit(event)}>
          <label className="field-label" htmlFor="deck-name">
            Deck name <span>Required</span>
          </label>
          <input
            autoFocus
            id="deck-name"
            className="form-input"
            type="text"
            placeholder="e.g. Spanish vocabulary"
            maxLength={100}
            required
            value={values.name}
            onChange={(event) =>
              setValues({ ...values, name: event.target.value })
            }
          />
          <label className="field-label description-label" htmlFor="deck-description">
            Description <span>Optional</span>
          </label>
          <textarea
            id="deck-description"
            className="form-input form-textarea"
            placeholder="What are you learning?"
            rows={3}
            maxLength={500}
            value={values.description}
            onChange={(event) =>
              setValues({ ...values, description: event.target.value })
            }
          />
          {error && <p className="form-error" role="alert">{error}</p>}
          <div className="dialog-actions">
            <button
              className="button button-secondary"
              type="button"
              onClick={closeDialog}
              disabled={saving}
            >
              Cancel
            </button>
            <button className="button button-primary" type="submit" disabled={saving}>
              {saving ? "Saving..." : deck ? "Save changes" : "Create deck"}
              {!saving && <Icon name="arrow" size={17} />}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

export default DeckFormDialog;
