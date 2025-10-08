import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { format } from 'date-fns'

interface Delivery {
  id: string
  farmer_code: string
  delivery_date: string
  quantity_liters: number
  quality_grade: string
  sync_status: string
}

export default function DeliveriesPage() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDeliveries()
  }, [])

  const loadDeliveries = async () => {
    try {
      const data = await api.getDeliveries()
      setDeliveries(data)
    } catch (error) {
      console.error('Failed to load deliveries:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="text-center py-12">Loading...</div>

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Milk Deliveries</h1>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4">Date</th>
                <th className="text-left py-3 px-4">Farmer Code</th>
                <th className="text-right py-3 px-4">Quantity (L)</th>
                <th className="text-left py-3 px-4">Grade</th>
                <th className="text-left py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {deliveries.map((delivery) => (
                <tr key={delivery.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">{delivery.delivery_date}</td>
                  <td className="py-3 px-4">{delivery.farmer_code}</td>
                  <td className="py-3 px-4 text-right">{delivery.quantity_liters}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-sm ${
                      delivery.quality_grade === 'A' ? 'bg-green-100 text-green-800' :
                      delivery.quality_grade === 'B' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {delivery.quality_grade}
                    </span>
                  </td>
                  <td className="py-3 px-4">{delivery.sync_status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
