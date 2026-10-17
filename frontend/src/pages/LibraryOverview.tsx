import Icon from "../components/Icon";

type LibraryOverviewProps = {
  deckCount: number;
  scheduledDeckCount: number;
  loading: boolean;
  onCreateDeck: () => void;
};

function LibraryOverview({
  deckCount,
  scheduledDeckCount,
  loading,
  onCreateDeck,
}: LibraryOverviewProps) {
  return (
    <section className="overview-grid" aria-label="Library overview">
      <div className="overview-card">
        <div className="overview-icon icon-lilac">
          <Icon name="layers" size={19} />
        </div>
        <div>
          <div className="overview-value">{loading ? "—" : deckCount}</div>
          <div className="overview-label">Total decks</div>
        </div>
        <div className="overview-detail">in your library</div>
      </div>
      <div className="overview-card">
        <div className="overview-icon icon-peach">
          <Icon name="book" size={19} />
        </div>
        <div>
          <div className="overview-value">
            {loading ? "—" : scheduledDeckCount}
          </div>
          <div className="overview-label">Scheduled decks</div>
        </div>
        <div className="overview-detail">review dates enabled</div>
      </div>
      <div className="overview-card overview-message">
        <div className="message-spark" aria-hidden="true">✳</div>
        <div>
          <div className="message-heading">Make it yours</div>
          <div className="message-copy">
            Create a deck for anything you want to learn.
          </div>
        </div>
        <button
          className="text-arrow"
          onClick={onCreateDeck}
          aria-label="Create your first deck"
        >
          <Icon name="arrow" size={19} />
        </button>
      </div>
    </section>
  );
}

export default LibraryOverview;
