import { useState } from 'react'
import { api } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function ReportsPage() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [reportData, setReportData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const loadReport = async () => {
    setLoading(true)
    try {
      const data = await api.getDailyReport(selectedDate)
      setReportData(data)
    } catch (error) {
      console.error('Failed to load report:', error)
    } finally {
      setLoading(false)
    }
  }

  const chartData = reportData?.station_totals?.map((st: any) => ({
    name: st.station_name,
    liters: parseFloat(st.total_liters),
    deliveries: st.delivery_count,
  })) || []

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Daily Reports</h1>

      <div className="card mb-6">
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="label">Select Date</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="input"
            />
          </div>
          <button
            onClick={loadReport}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Loading...' : 'Generate Report'}
          </button>
        </div>
      </div>

      {reportData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="card">
              <p className="text-gray-600 mb-2">Total Deliveries</p>
              <p className="text-3xl font-bold">{reportData.overall_delivery_count}</p>
            </div>
            <div className="card">
              <p className="text-gray-600 mb-2">Total Volume</p>
              <p className="text-3xl font-bold">{reportData.overall_total_liters.toFixed(1)}L</p>
            </div>
            <div className="card">
              <p className="text-gray-600 mb-2">Stations</p>
              <p className="text-3xl font-bold">{reportData.station_totals.length}</p>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-bold mb-4">Volume by Station</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="liters" fill="#2E7D32" name="Liters" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  )
}
