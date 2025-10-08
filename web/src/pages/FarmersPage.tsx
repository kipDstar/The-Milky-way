import { useEffect, useState } from 'react'
import { api } from '../services/api'

interface Farmer {
  id: string
  farmer_code: string
  name: string
  phone: string
  is_active: boolean
}

export default function FarmersPage() {
  const [farmers, setFarmers] = useState<Farmer[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFarmers()
  }, [])

  const loadFarmers = async () => {
    try {
      const data = await api.getFarmers()
      setFarmers(data)
    } catch (error) {
      console.error('Failed to load farmers:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="text-center py-12">Loading...</div>

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Farmers</h1>
        <button className="btn-primary">Add New Farmer</button>
      </div>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4">Code</th>
                <th className="text-left py-3 px-4">Name</th>
                <th className="text-left py-3 px-4">Phone</th>
                <th className="text-left py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {farmers.map((farmer) => (
                <tr key={farmer.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium">{farmer.farmer_code}</td>
                  <td className="py-3 px-4">{farmer.name}</td>
                  <td className="py-3 px-4">{farmer.phone}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-sm ${
                      farmer.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {farmer.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
