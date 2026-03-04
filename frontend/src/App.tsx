import { MapViewer } from "./components/Map/MapViewer";

function App() {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <header
        style={{
          padding: "0.75rem 1rem",
          borderBottom: "1px solid #e0e0e0",
          background: "#f5f5f5",
        }}
      >
        <h1 style={{ margin: 0, fontSize: "1.25rem" }}>
          GeoSpatial Data Quality Agent
        </h1>
      </header>
      <main style={{ flex: 1, minHeight: 0 }}>
        <MapViewer />
      </main>
    </div>
  );
}

export default App;
