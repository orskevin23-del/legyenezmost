import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import LanguageSwitcher from './components/LanguageSwitcher';

// Layouts
import DashboardLayout from './layouts/DashboardLayout';

// Auth Pages
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import ForgotPassword from './pages/Auth/ForgotPassword';
import ResetPassword from './pages/Auth/ResetPassword';

// Dashboard Pages
import DashboardOverview from './pages/Dashboard/Overview';
import ScriptGenerator from './pages/Dashboard/ScriptGenerator';
import NotionAnalytics from './pages/Dashboard/NotionAnalytics';
import HookLibrary from './pages/Dashboard/HookLibrary';
import VideoFactory from './pages/Dashboard/VideoFactory';
import Analytics from './pages/Dashboard/Analytics';
import Settings from './pages/Dashboard/Settings';

import './App.css';

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <BrowserRouter>
          <LanguageSwitcher />
          <Routes>
            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />

            {/* Dashboard Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardOverview />} />
              <Route path="scripts" element={<ScriptGenerator />} />
              <Route path="hooks" element={<HookLibrary />} />
              <Route path="videos" element={<VideoFactory />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="notion-analytics" element={<NotionAnalytics />} />
              <Route path="settings" element={<Settings />} />
            </Route>

            {/* Redirect root to dashboard or login */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          
          <Toaster 
            position="top-right"
            theme="dark"
            richColors
          />
        </BrowserRouter>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
