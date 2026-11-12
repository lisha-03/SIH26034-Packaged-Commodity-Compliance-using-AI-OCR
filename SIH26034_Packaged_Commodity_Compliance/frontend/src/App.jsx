import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './AuthContext'
import Layout from './components/Layout'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ScanProduct from './pages/ScanProduct'
import InspectionDetail from './pages/InspectionDetail'
import InspectionHistory from './pages/InspectionHistory'
import UserManagement from './pages/UserManagement'
import Settings from './pages/Settings'

function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && user.role !== 'admin') return <Navigate to="/dashboard" replace />
  return <Layout>{children}</Layout>
}

function AppRoutes() {
  const { user, loading } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={loading ? null : (user ? <Navigate to="/dashboard" replace /> : <Login />)} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/scan" element={<ProtectedRoute><ScanProduct /></ProtectedRoute>} />
      <Route path="/inspections/:id" element={<ProtectedRoute><InspectionDetail /></ProtectedRoute>} />
      <Route path="/history" element={<ProtectedRoute><InspectionHistory /></ProtectedRoute>} />
      <Route path="/users" element={<ProtectedRoute adminOnly><UserManagement /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
