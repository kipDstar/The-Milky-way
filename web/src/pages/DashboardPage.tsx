import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { TrendingUp, Users, Package, DollarSign } from 'lucide-react'

interface DashboardStats {
  todayDeliveries: number
  todayLiters: number
  activeFarmers: number
  pendingPayments: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    todayDeliveries: 0,
    todayLiters: 0,
    activeFarmers: 0,
    pendingPayments: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const today = new Date().toISOString().split('T')[0]
      
      // Load today's deliveries
      const deliveries = await api.getDeliveries({ date: today })
      
      const todayDeliveries = deliveries.length
      const todayLiters = deliveries.reduce(
        (sum: number, d: any) => sum + parseFloat(d.quantity_liters),
        0
      )

      setStats({
        todayDeliveries,
        todayLiters,
        activeFarmers: 150, // TODO: Fetch from API
        pendingPayments: 45, // TODO: Fetch from API
      })
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: 'Today\'s Deliveries',
      value: stats.todayDeliveries,
      icon: Package,
      color: 'bg-blue-500',
    },
    {
      title: 'Today\'s Volume',
      value: `${stats.todayLiters.toFixed(1)}L`,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      title: 'Active Farmers',
      value: stats.activeFarmers,
      icon: Users,
      color: 'bg-purple-500',
    },
    {
      title: 'Pending Payments',
      value: stats.pendingPayments,
      icon: DollarSign,
      color: 'bg-orange-500',
    },
  ]

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat) => (
          <div key={stat.title} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">{stat.title}</p>
                <p className="text-3xl font-bold">{stat.value}</p>
              </div>
              <div className={`${stat.color} text-white p-4 rounded-lg`}>
                <stat.icon size={24} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
          <div className="space-y-2">
            <button className="btn-primary w-full text-left">
              Record New Delivery
            </button>
            <button className="btn-secondary w-full text-left">
              View Daily Report
            </button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
          <p className="text-gray-600">No recent activity to display</p>
        </div>
      </div>
    </div>
  )
}
