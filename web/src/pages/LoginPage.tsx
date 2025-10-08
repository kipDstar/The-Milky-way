import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../services/AuthContext'
import { Milk } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const success = await login(email, password)
    
    if (success) {
      navigate('/')
    } else {
      setError('Invalid email or password')
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center p-4">
      <div className="card max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary text-white rounded-full mb-4">
            <Milk size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">DDCPTS</h1>
          <p className="text-gray-600 mt-2">Dairy Collection & Payment System</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="label">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              placeholder="officer@example.com"
              required
            />
          </div>

          <div>
            <label className="label">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>

          <div className="bg-blue-50 px-4 py-3 rounded-lg text-sm">
            <p className="font-semibold text-blue-900 mb-2">Demo Credentials:</p>
            <p className="text-blue-700">
              <strong>Officer:</strong> officer@ddcpts.test / Officer@123
            </p>
            <p className="text-blue-700">
              <strong>Manager:</strong> manager@ddcpts.test / Manager@123
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}
