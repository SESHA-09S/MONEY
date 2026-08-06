import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, TrendingUp, TrendingDown, Users, CreditCard,
  Activity, Brain, AlertTriangle, Lightbulb, FileText, Settings,
  User, ShieldCheck, LogOut, Zap, Menu, X, ChevronLeft,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/store/authStore'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, href: '/dashboard' },
  { label: 'Income', icon: TrendingUp, href: '/income' },
  { label: 'Expenses', icon: TrendingDown, href: '/expenses' },
  { label: 'Customers', icon: Users, href: '/customers' },
  { label: 'Customer Dues', icon: CreditCard, href: '/customers/dues' },
  { label: 'Cash Flow', icon: Activity, href: '/cashflow' },
  { label: 'AI Predictions', icon: Brain, href: '/predictions' },
  { label: 'Risk Dashboard', icon: AlertTriangle, href: '/risk' },
  { label: 'Recommendations', icon: Lightbulb, href: '/recommendations' },
  { label: 'Reports', icon: FileText, href: '/reports' },
]

const bottomItems = [
  { label: 'Settings', icon: Settings, href: '/settings' },
  { label: 'Profile', icon: User, href: '/profile' },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const { user, logout } = useAuthStore()

  return (
    <aside
      className={cn(
        'flex flex-col h-screen bg-card border-r border-border transition-all duration-300 ease-in-out sticky top-0',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
              <Zap className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="font-bold text-sm leading-none gradient-text">SmartCash</p>
              <p className="text-xs text-muted-foreground">AI Platform</p>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center mx-auto">
            <Zap className="h-4 w-4 text-white" />
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className={cn('h-7 w-7', collapsed && 'mx-auto')}
        >
          {collapsed ? <Menu className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                'text-muted-foreground hover:text-foreground hover:bg-accent',
                isActive && 'bg-primary/10 text-primary hover:bg-primary/15',
                collapsed && 'justify-center px-2'
              )
            }
            title={collapsed ? item.label : undefined}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}

        {/* Admin section */}
        {user?.role === 'admin' && (
          <>
            <div className={cn('px-3 py-1 mt-4', collapsed && 'hidden')}>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Admin</p>
            </div>
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                  'text-muted-foreground hover:text-foreground hover:bg-accent',
                  isActive && 'bg-primary/10 text-primary',
                  collapsed && 'justify-center px-2'
                )
              }
            >
              <ShieldCheck className="h-4 w-4 shrink-0" />
              {!collapsed && <span>Admin Panel</span>}
            </NavLink>
          </>
        )}
      </nav>

      {/* Bottom section */}
      <div className="p-2 space-y-1 border-t border-border">
        {bottomItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                'text-muted-foreground hover:text-foreground hover:bg-accent',
                isActive && 'bg-primary/10 text-primary',
                collapsed && 'justify-center px-2'
              )
            }
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
        <button
          onClick={logout}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
            'text-muted-foreground hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30',
            collapsed && 'justify-center px-2'
          )}
          title={collapsed ? 'Logout' : undefined}
        >
          <LogOut className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>

        {/* User avatar */}
        {!collapsed && user && (
          <div className="flex items-center gap-2 px-3 py-2 mt-2 rounded-lg bg-muted">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center text-white text-xs font-semibold">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">{user.full_name}</p>
              <p className="text-xs text-muted-foreground truncate">{user.role}</p>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}
