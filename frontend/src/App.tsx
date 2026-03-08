import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppProvider } from "./context/AppContext";
import { AppLayout } from "./components/Layout/AppLayout";
import { UploadPage } from "./pages/UploadPage";
import { MapPage } from "./pages/MapPage";
import { StatusPage } from "./pages/StatusPage";

function App() {
  return (
    <AppProvider>
      <HashRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Navigate to="/upload" replace />} />
            <Route path="upload" element={<UploadPage />} />
            <Route path="map" element={<MapPage />} />
            <Route path="status" element={<StatusPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/upload" replace />} />
        </Routes>
      </HashRouter>
    </AppProvider>
  );
}

export default App;
