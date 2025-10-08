import { Outlet, NavLink } from 'react-router-dom'
import { Home, Package, Users, FileText, LogOut } from 'lucide-react'
import { useAuth } from '../services/AuthContext'

export default function Layout() {
  const { logout } = useAuth()

  const navItems = [
    { to: '/', label: 'Dashboard', icon: Home },
    { to: '/deliveries', label: 'Deliveries', icon: Package },
    { to: '/farmers', label: 'Farmers', icon: Users },
    { to: '/reports', label: 'Reports', icon: FileText },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-primary text-white shadow-lg">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">DDCPTS Dashboard</h1>
          <button
            onClick={logout}
            className="flex items-center gap-2 px-4 py-2 bg-primary-dark rounded-lg hover:bg-opacity-80 transition-colors"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4">
          <div className="flex gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-4 py-3 transition-colors ${
                    isActive
                      ? 'text-primary border-b-2 border-primary font-medium'
                      : 'text-gray-600 hover:text-primary'
                  }`
                }
              >
                <Icon size={20} />
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
