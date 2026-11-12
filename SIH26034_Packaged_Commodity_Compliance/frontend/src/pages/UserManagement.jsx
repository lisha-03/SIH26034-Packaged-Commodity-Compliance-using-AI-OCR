import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api'
import { useAuth } from '../AuthContext'

export default function UserManagement() {
  const { user } = useAuth()
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')
  const [formError, setFormError] = useState('')
  const [formSuccess, setFormSuccess] = useState('')
  const [form, setForm] = useState({ username: '', password: '', full_name: '', role: 'officer' })
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    api.get('/users')
      .then(res => setUsers(res.data))
      .catch(err => setError(errorMessage(err, 'Could not load users.')))
  }

  useEffect(load, [])

  const handleChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError('')
    setFormSuccess('')
    setSubmitting(true)
    try {
      await api.post('/users', form)
      setFormSuccess(`User "${form.username}" created.`)
      setForm({ username: '', password: '', full_name: '', role: 'officer' })
      load()
    } catch (err) {
      setFormError(errorMessage(err, 'Could not create user.'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id, username) => {
    if (!window.confirm(`Delete user "${username}"? This cannot be undone.`)) return
    try {
      await api.delete(`/users/${id}`)
      load()
    } catch (err) {
      setError(errorMessage(err, 'Could not delete user.'))
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-navy-900 mb-1">User Management</h1>
      <p className="text-gray-500 text-sm mb-6">Admin-only. Create and remove Admin / Enforcement Officer accounts.</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-1 h-fit">
          <h3 className="font-semibold text-gray-700 mb-3">Add New User</h3>
          {formError && <div className="mb-3 text-xs bg-red-50 border border-red-200 text-red-700 rounded-lg px-3 py-2">{formError}</div>}
          {formSuccess && <div className="mb-3 text-xs bg-green-50 border border-green-200 text-green-700 rounded-lg px-3 py-2">{formSuccess}</div>}
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="label-text">Full Name</label>
              <input className="input-field" value={form.full_name} onChange={e => handleChange('full_name', e.target.value)} required />
            </div>
            <div>
              <label className="label-text">Username</label>
              <input className="input-field" value={form.username} onChange={e => handleChange('username', e.target.value)} required />
            </div>
            <div>
              <label className="label-text">Password</label>
              <input type="password" className="input-field" value={form.password} onChange={e => handleChange('password', e.target.value)} required minLength={6} />
            </div>
            <div>
              <label className="label-text">Role</label>
              <select className="input-field" value={form.role} onChange={e => handleChange('role', e.target.value)}>
                <option value="officer">Enforcement Officer</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <button type="submit" disabled={submitting} className="btn-primary w-full justify-center flex">
              {submitting ? 'Creating…' : 'Create User'}
            </button>
          </form>
        </div>

        <div className="card lg:col-span-2">
          <h3 className="font-semibold text-gray-700 mb-3">All Users</h3>
          {error && <div className="text-red-600 text-sm mb-3">{error}</div>}
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-400 uppercase tracking-wide border-b">
                <th className="py-2">Name</th>
                <th className="py-2">Username</th>
                <th className="py-2">Role</th>
                <th className="py-2">Created</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="border-b last:border-0">
                  <td className="py-2.5 font-medium text-gray-800">{u.full_name}</td>
                  <td className="py-2.5 text-gray-500">{u.username}</td>
                  <td className="py-2.5 capitalize">{u.role}</td>
                  <td className="py-2.5 text-gray-400 text-xs">{u.created_at}</td>
                  <td className="py-2.5 text-right">
                    {u.id !== user?.id && (
                      <button onClick={() => handleDelete(u.id, u.username)} className="text-red-600 hover:underline text-xs font-semibold">
                        Delete
                      </button>
                    )}
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
