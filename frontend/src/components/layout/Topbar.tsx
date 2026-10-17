function Topbar() {
  return (
    <header className="topbar">
      <div className="breadcrumb">
        <span>Workspace</span>
        <span className="crumb-slash">/</span>
        <strong>My library</strong>
      </div>
      <div className="topbar-note"><span className="online-dot" /> Your learning space</div>
    </header>
  );
}

export default Topbar;
