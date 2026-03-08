import { Outlet, NavLink } from "react-router-dom";
import {
  CalciteShell,
  CalciteShellPanel,
  CalciteNavigation,
  CalciteNavigationLogo,
} from "@esri/calcite-components-react";

export function AppLayout() {
  return (
    <CalciteShell>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <div slot="header">
        <CalciteNavigation label="Main navigation">
          <CalciteNavigationLogo slot="logo" heading="GeoSpatial Data Quality Agent" />
          <nav slot="content-start" className="app-nav" aria-label="Main navigation">
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
        </CalciteNavigation>
      </div>
      <CalciteShellPanel slot="panel-start" position="start" displayMode="dock">
        <div className="app-panel-content">
          <p className="app-panel-title">Dataset</p>
          <p className="app-panel-hint">Upload a shapefile or GeoJSON on the Upload page.</p>
        </div>
      </CalciteShellPanel>
      <div className="app-main" id="main-content" role="main" style={{ minHeight: "400px" }}>
        <Outlet />
      </div>
    </CalciteShell>
  );
}
