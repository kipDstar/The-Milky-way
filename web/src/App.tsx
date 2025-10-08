import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './services/AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import DeliveriesPage from './pages/DeliveriesPage'
import FarmersPage from './pages/FarmersPage'
import ReportsPage from './pages/ReportsPage'
import Layout from './components/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="deliveries" element={<DeliveriesPage />} />
          <Route path="farmers" element={<FarmersPage />} />
          <Route path="reports" element={<ReportsPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
