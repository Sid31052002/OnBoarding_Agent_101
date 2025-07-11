import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import RegisterPage from "./RegisterPage";
import DashboardPage from "./DashboardPage";
import AdminDashboardPage from "./AdminDashboardPage"; // Add this import

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RegisterPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/admin" element={<AdminDashboardPage />} /> {/* Add this route */}
      </Routes>
    </Router>
  );
}

export default App;
