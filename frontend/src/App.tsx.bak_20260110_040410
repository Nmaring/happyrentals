import { Navigate, Route, Routes } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Properties from "./pages/Properties";

import { useAuth } from "./providers/AuthProvider";
import Header from "./components/Header.jsx";

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { token, loading } = useAuth();

  if (loading) return <div style={{ padding: 20 }}>Loadingâ€¦</div>;
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function AuthedLayout({ children }: { children: JSX.Element }) {
  return (
    <>
      <Header />
      {children}
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/properties" replace />} />

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/properties"
        element={
          <ProtectedRoute>
            <AuthedLayout>
              <Properties />
            </AuthedLayout>
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/properties" replace />} />
    </Routes>
  );
}



