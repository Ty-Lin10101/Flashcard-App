import Icon from "../Icon";

function Sidebar({ deckCount }: { deckCount: number }) {
  return (
    <aside className="sidebar">
      <a className="brand" href="#" aria-label="Recall home">
        <span className="brand-mark"><Icon name="layers" size={21} /></span>
        <span>recall<span className="brand-period">.</span></span>
      </a>

      <div className="sidebar-label">Workspace</div>
      <nav className="primary-nav" aria-label="Main navigation">
        <a className="nav-item active" href="#library" aria-current="page">
          <Icon name="grid" size={19} />
          <span>My library</span>
          <span className="nav-count">{deckCount}</span>
        </a>
        <a
          className="nav-item disabled"
          href="#library"
          aria-disabled="true"
          onClick={(event) => event.preventDefault()}
        >
          <Icon name="settings" size={19} />
          <span>Settings</span>
          <span className="soon-label">Soon</span>
        </a>
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-tip">
          <div className="tip-icon"><Icon name="book" size={18} /></div>
          <p className="tip-title">Small steps add up.</p>
          <p className="tip-copy">A little practice each day makes a big difference.</p>
        </div>
        <div className="profile">
          <div className="avatar">R</div>
          <div className="profile-copy">
            <span className="profile-name">My workspace</span>
            <span className="profile-caption">Personal library</span>
          </div>
          <span className="profile-dot" aria-label="Workspace active" />
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
