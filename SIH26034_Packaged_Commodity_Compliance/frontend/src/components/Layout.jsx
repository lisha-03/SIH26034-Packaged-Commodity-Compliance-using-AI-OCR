import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import AIAssistant from './AIAssistant'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/scan', label: 'Scan Product', icon: '📷' },
  { to: '/history', label: 'Inspection History', icon: '🗂️' },
  { to: '/users', label: 'User Management', icon: '👥', adminOnly: true },
  { to: '/settings', label: 'Settings / About', icon: '⚙️' },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex bg-gray-50">
      <aside className="w-64 bg-navy-950 text-white flex flex-col shrink-0">
        <div className="px-5 py-6 border-b border-white/10">
          <div className="text-xs uppercase tracking-widest text-blue-300 font-semibold">SIH26034</div>
          <div className="text-lg font-bold leading-tight mt-1">Packaged Commodity<br />Compliance</div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(item => {
            if (item.adminOnly && user?.role !== 'admin') return null
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive ? 'bg-navy-700 text-white' : 'text-blue-100/80 hover:bg-navy-800'
                  }`
                }
              >
                <span>{item.icon}</span>
                {item.label}
              </NavLink>
            )
          })}
        </nav>
        <div className="px-4 py-4 border-t border-white/10">
          <div className="text-sm font-semibold">{user?.full_name}</div>
          <div className="text-xs text-blue-200 uppercase tracking-wide">{user?.role}</div>
          <button
            onClick={handleLogout}
            className="mt-3 w-full text-sm bg-white/10 hover:bg-white/20 rounded-lg py-2 transition-colors"
          >
            Log Out
          </button>
        </div>
      </aside>
      <main className="flex-1 min-w-0">
        <div className="max-w-6xl mx-auto px-6 py-8">{children}</div>
      </main>
      <AIAssistant />
    </div>
  )
}
