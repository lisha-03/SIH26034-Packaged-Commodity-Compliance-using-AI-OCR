import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import api, { errorMessage } from '../api'
import StatusBadge from '../components/StatusBadge'

const STATUS_COLORS = { COMPLIANT: '#16a34a', NEEDS_REVIEW: '#ca8a04', NON_COMPLIANT: '#dc2626' }

function StatCard({ label, value, sublabel }) {
  return (
    <div className="card">
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{label}</div>
      <div className="text-3xl font-bold text-navy-900 mt-2">{value}</div>
      {sublabel && <div className="text-xs text-gray-400 mt-1">{sublabel}</div>}
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  const load = () => {
    api.get('/dashboard/stats')
      .then(res => setStats(res.data))
      .catch(err => setError(errorMessage(err, 'Could not load dashboard data.')))
  }

  useEffect(load, [])

  if (error) return <div className="text-red-600">{error}</div>
  if (!stats) return <div className="text-gray-500">Loading dashboard…</div>

  const pieData = stats.status_breakdown.map(s => ({
    name: s.overall_status.replace('_', ' '),
    value: s.count,
    key: s.overall_status,
  }))

  return (
    <div>
      <h1 className="text-2xl font-bold text-navy-900 mb-1">Enforcement Dashboard</h1>
      <p className="text-gray-500 text-sm mb-6">Live compliance-screening statistics from the inspection database.</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Scanned" value={stats.total_scanned} />
        <StatCard label="Compliant" value={stats.compliant} />
        <StatCard label="Non-Compliant" value={stats.non_compliant} />
        <StatCard label="Needs Review" value={stats.needs_review} />
        <StatCard label="Total Violations" value={stats.total_violations} />
        <StatCard label="Compliance %" value={`${stats.compliance_percentage}%`} />
        <StatCard label="Avg. Score" value={stats.average_score} sublabel="out of 100" />
        <Link to="/scan" className="card flex flex-col items-center justify-center text-center hover:border-navy-700 transition-colors">
          <div className="text-2xl">📷</div>
          <div className="text-sm font-semibold text-navy-800 mt-1">Scan New Product</div>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-3">Status Breakdown</h3>
          {pieData.length === 0 ? (
            <div className="text-sm text-gray-400 py-10 text-center">No inspections yet. Scan a product to see data here.</div>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={3}>
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={STATUS_COLORS[entry.key] || '#94a3b8'} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-3">Common Violation Categories</h3>
          {stats.common_violations.length === 0 ? (
            <div className="text-sm text-gray-400 py-10 text-center">No violations recorded yet.</div>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={stats.common_violations} layout="vertical" margin={{ left: 10, right: 10 }}>
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="rule_title" width={140} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#1d3a5f" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-700 mb-3">Recent Inspections</h3>
        {stats.recent_inspections.length === 0 ? (
          <div className="text-sm text-gray-400 py-6 text-center">No inspections yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-400 uppercase tracking-wide border-b">
                <th className="py-2">Product</th>
                <th className="py-2">Scanned At</th>
                <th className="py-2">Score</th>
                <th className="py-2">Status</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_inspections.map(r => (
                <tr key={r.inspection_id} className="border-b last:border-0">
                  <td className="py-2.5 font-medium text-gray-800">{r.product_name}</td>
                  <td className="py-2.5 text-gray-500">{r.scanned_at}</td>
                  <td className="py-2.5">{r.compliance_score}/100</td>
                  <td className="py-2.5"><StatusBadge status={r.overall_status} /></td>
                  <td className="py-2.5 text-right">
                    <Link to={`/inspections/${r.inspection_id}`} className="text-navy-700 hover:underline text-xs font-semibold">
                      View →
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
