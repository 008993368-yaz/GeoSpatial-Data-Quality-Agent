import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppProvider } from "./context/AppContext";
import { AppLayout } from "./components/Layout/AppLayout";
import { UploadPage } from "./pages/UploadPage";
import { MapPage } from "./pages/MapPage";
import { StatusPage } from "./pages/StatusPage";
import { DashboardPage } from "./components/Dashboard/DashboardPage";

function App() {
  return (
    <AppProvider>
      <HashRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="upload" element={<UploadPage />} />
            <Route path="map" element={<MapPage />} />
            <Route path="status" element={<StatusPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </HashRouter>
    </AppProvider>
  );
}

export default App;
