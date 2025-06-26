// FILE: src/App.jsx

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import './index.css';

// DASHBOARD COMPONENT
const Dashboard = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#f9fafb' }}>

      {/* NAVIGATION */}
      <nav className="navbar">
        <div className="navbar-content">
          <h1>Medical Notes Cleaner</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span>Welcome, {user?.full_name}</span>
            <button onClick={logout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* MAIN CONTENT */}
      <main className="container" style={{ paddingTop: '2rem' }}>

        {/* WELCOME CARD */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2>Welcome to Your Medical Notes Dashboard</h2>
          <p>
            Transform messy medical documentation into clean, professional notes
            using AI-powered processing.
          </p>

          <div className="alert alert-success">
            🎉 <strong>Authentication Working!</strong> You are logged in as {user?.email}
          </div>
        </div>

        {/* NOTES PROCESSING AREA */}
        <div className="card">
          <h3>Process Medical Notes</h3>
          <p style={{ marginBottom: '1rem' }}>
            Enter your raw medical notes below and our AI will clean and format them.
          </p>

          {/* NOTE INPUT */}
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="noteInput">Raw Medical Note</label>
            <textarea
              id="noteInput"
              className="input-field"
              rows="4"
              placeholder="Example: pt c/o cp x3d, worsening w/ exertion. PE: hr 95, bp 140/90..."
              style={{ resize: 'vertical', minHeight: '100px' }}
            />
          </div>

          {/* PROCESS BUTTON */}
          <button className="btn-primary" style={{ marginBottom: '1rem' }}>
            Clean Note
          </button>

          {/* PLACEHOLDER FOR RESULTS */}
          <div className="alert alert-info">
            <strong>Coming Next:</strong> AI note processing will connect to your Lambda backend
            with Bedrock integration. For now, this demonstrates the complete authentication flow.
          </div>
        </div>

        {/* USER INFO CARD */}
        <div className="card" style={{ marginTop: '2rem' }}>
          <h3>Your Account</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <strong>Email:</strong><br />
              {user?.email}
            </div>
            <div>
              <strong>User ID:</strong><br />
              {user?.id}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

// PROTECTED ROUTE WRAPPER
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

// MAIN APP
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;