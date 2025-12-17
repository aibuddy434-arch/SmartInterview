import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import InterviewCreator from './pages/InterviewCreator';
import InterviewList from './pages/InterviewList';
import CandidateList from './pages/CandidateList';
import InterviewSession from './pages/InterviewSession';
import PublicInterview from './pages/PublicInterview';
import InterviewReports from './pages/InterviewReports';
import ReportDetail from './pages/ReportDetail';

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
          <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" />} />
          <Route path="/interview/:interviewId" element={<PublicInterview />} />

          {/* Protected routes */}
          <Route path="/" element={user ? <Layout /> : <Navigate to="/login" />}>
            <Route index element={<Navigate to="/dashboard" />} />
            <Route path="dashboard" element={<Dashboard />} />

            {/* Admin/Interviewer routes */}
            {user && (user.role === 'admin' || user.role === 'interviewer') && (
              <>
                <Route path="admin" element={<AdminDashboard />} />
                <Route path="interviews/create" element={<InterviewCreator />} />
                <Route path="interviews" element={<InterviewList />} />
                <Route path="candidates" element={<CandidateList />} />
                <Route path="reports" element={<InterviewReports />} />
                <Route path="reports/:sessionId" element={<ReportDetail />} />
              </>
            )}

            {/* Admin only routes */}
            {user && user.role === 'admin' && (
              <>
                <Route path="admin/users" element={<div>User Management</div>} />
                <Route path="admin/settings" element={<div>System Settings</div>} />
              </>
            )}

            {/* Interview session route */}
            <Route path="session/:sessionId" element={<InterviewSession />} />
          </Route>

          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;


