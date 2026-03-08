import { Outlet, NavLink } from "react-router-dom";

export function AppLayout() {
  return (
    <div className="app-layout">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <header className="app-header" role="banner">
        <h1 className="app-title">GeoSpatial Data Quality Agent</h1>
        <nav className="app-nav" aria-label="Main navigation">
          <NavLink
            to="/upload"
            className={({ isActive }) => `app-nav-link${isActive ? " app-nav-link--active" : ""}`}
            end
          >
            Upload
          </NavLink>
          <NavLink
            to="/map"
            className={({ isActive }) => `app-nav-link${isActive ? " app-nav-link--active" : ""}`}
          >
            Map
          </NavLink>
          <NavLink
            to="/status"
            className={({ isActive }) => `app-nav-link${isActive ? " app-nav-link--active" : ""}`}
          >
            Status
          </NavLink>
        </nav>
      </header>
      <main className="app-main" id="main-content" role="main">
        <Outlet />
      </main>
    </div>
  );
}
