import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api, { errorMessage } from '../api'
import StatusBadge from '../components/StatusBadge'

export default function InspectionHistory() {
  const [rows, setRows] = useState([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.get('/history', { params: { search, status } })
      .then(res => setRows(res.data))
      .catch(err => setError(errorMessage(err, 'Could not load inspection history.')))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    load()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-navy-900 mb-1">Inspection History</h1>
      <p className="text-gray-500 text-sm mb-6">Persistent repository of every scanned product and its compliance result.</p>

      <form onSubmit={handleSearchSubmit} className="flex flex-wrap gap-3 mb-5">
        <input
          className="input-field max-w-xs"
          placeholder="Search by product name…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select className="input-field max-w-[200px]" value={status} onChange={e => setStatus(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="COMPLIANT">Compliant</option>
          <option value="NEEDS_REVIEW">Needs Review</option>
          <option value="NON_COMPLIANT">Non-Compliant</option>
        </select>
        <button type="submit" className="btn-primary">Filter</button>
      </form>

      {error && <div className="text-red-600 text-sm mb-4">{error}</div>}

      <div className="card">
        {loading ? (
          <div className="text-sm text-gray-400 py-8 text-center">Loading…</div>
        ) : rows.length === 0 ? (
          <div className="text-sm text-gray-400 py-8 text-center">No inspections found.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-400 uppercase tracking-wide border-b">
                <th className="py-2">Product</th>
                <th className="py-2">Officer</th>
                <th className="py-2">Scanned At</th>
                <th className="py-2">Score</th>
                <th className="py-2">Status</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <tr key={r.inspection_id} className="border-b last:border-0">
                  <td className="py-2.5 font-medium text-gray-800">
                    {r.product_name}
                    {r.is_demo === 1 && <span className="ml-2 text-[10px] text-gray-400 border rounded-full px-1.5 py-0.5">DEMO</span>}
                  </td>
                  <td className="py-2.5 text-gray-500">{r.officer_name}</td>
                  <td className="py-2.5 text-gray-500">{r.scanned_at}</td>
                  <td className="py-2.5">{r.compliance_score}/100</td>
                  <td className="py-2.5"><StatusBadge status={r.overall_status} /></td>
                  <td className="py-2.5 text-right">
                    <Link to={`/inspections/${r.inspection_id}`} className="text-navy-700 hover:underline text-xs font-semibold">
                      View Report →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
