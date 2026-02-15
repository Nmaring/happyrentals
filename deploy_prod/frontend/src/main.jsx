import "./setupFetchAuth";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./index.css";

ReactDOM.saasBoot().then(() => {
  createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthGate><AuthGate><App /></AuthGate></AuthGate>
    </BrowserRouter>
  </React.StrictMode>
);
});




