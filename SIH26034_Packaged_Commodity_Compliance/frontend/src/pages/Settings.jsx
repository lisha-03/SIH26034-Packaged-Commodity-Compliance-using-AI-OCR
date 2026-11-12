import { useAuth } from '../AuthContext'

export default function Settings() {
  const { user } = useAuth()

  return (
    <div>
      <h1 className="text-2xl font-bold text-navy-900 mb-1">Settings / About</h1>
      <p className="text-gray-500 text-sm mb-6">System information and disclaimer.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-3">Account</h3>
          <div className="text-sm space-y-1">
            <div><span className="text-gray-400">Name:</span> {user?.full_name}</div>
            <div><span className="text-gray-400">Username:</span> {user?.username}</div>
            <div><span className="text-gray-400">Role:</span> <span className="capitalize">{user?.role}</span></div>
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-3">About This System</h3>
          <p className="text-sm text-gray-600">
            SIH26034 — Packaged Commodity Compliance is an AI-assisted screening
            prototype built for the Smart India Hackathon. It uses OCR (Tesseract)
            to read packaged-commodity labels, extracts mandatory declarations,
            and checks them against a rule engine based on the Legal Metrology
            (Packaged Commodities) Rules, 2011.
          </p>
        </div>

        <div className="card lg:col-span-2 bg-amber-50 border-amber-200">
          <h3 className="font-semibold text-amber-800 mb-2">⚠ Important Disclaimer</h3>
          <p className="text-sm text-amber-800">
            This system provides <b>AI-assisted compliance screening only</b>. It does
            not make a final legal determination of non-compliance. Every flagged
            issue must be verified by an authorized Legal Metrology enforcement
            officer against the current text of the Legal Metrology Act, 2009 and
            the Legal Metrology (Packaged Commodities) Rules, 2011 before any
            enforcement action is taken. The reference file supplied with this
            project was a links/navigation page rather than the full statutory
            text — see <code className="text-xs bg-white px-1 rounded">docs/compliance_rules.md</code> for sourcing details.
          </p>
        </div>
      </div>
    </div>
  )
}
