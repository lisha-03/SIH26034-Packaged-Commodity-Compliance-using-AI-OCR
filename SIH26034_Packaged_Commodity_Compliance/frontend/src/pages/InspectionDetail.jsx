import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api, { errorMessage } from '../api'
import StatusBadge from '../components/StatusBadge'

const FIELD_LABELS = {
  product_name: 'Product Name',
  manufacturer: 'Manufacturer / Packer / Importer',
  address: 'Address',
  net_quantity: 'Net Quantity',
  mrp: 'MRP',
  mfg_date: 'Mfg / Packing Date',
  consumer_care: 'Consumer Care',
  other_declarations: 'Other Declarations',
}

export default function InspectionDetail() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get(`/inspections/${id}`)
      .then(res => setData(res.data))
      .catch(err => setError(errorMessage(err, 'Could not load inspection.')))
  }, [id])

  if (error) return <div className="text-red-600">{error}</div>
  if (!data) return <div className="text-gray-500">Loading…</div>

  const { inspection, declarations, violations, report_available } = data
  const scoreColor = inspection.compliance_score >= 85 ? 'text-green-600'
    : inspection.compliance_score >= 50 ? 'text-yellow-600' : 'text-red-600'

  return (
    <div>
      <div className="flex items-start justify-between mb-6">
        <div>
          <Link to="/history" className="text-xs text-navy-700 font-semibold hover:underline">← Back to History</Link>
          <h1 className="text-2xl font-bold text-navy-900 mt-1">{inspection.product_name}</h1>
          <p className="text-gray-500 text-sm">Inspection #{inspection.id} · Scanned {inspection.scanned_at} · Officer: {inspection.officer_name}</p>
        </div>
        {report_available && (
          <a href={`/api/inspections/${id}/report`} target="_blank" rel="noreferrer" className="btn-primary">
            Download PDF Report
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="card lg:col-span-1 flex flex-col items-center justify-center text-center">
          <div className="text-xs text-gray-400 uppercase font-semibold tracking-wide">Compliance Score</div>
          <div className={`text-5xl font-extrabold mt-2 ${scoreColor}`}>{inspection.compliance_score}</div>
          <div className="text-xs text-gray-400 mb-3">out of 100</div>
          <StatusBadge status={inspection.overall_status} />
          {inspection.is_demo === 1 && (
            <div className="mt-3 text-[10px] uppercase tracking-wide text-gray-400 border rounded-full px-2 py-0.5">Demo / Synthetic Product</div>
          )}
        </div>

        <div className="card lg:col-span-2">
          <div className="text-xs text-gray-400 uppercase font-semibold tracking-wide mb-2">Scanned Image</div>
          <img
            src={`/api/inspections/${id}/image`}
            alt="scanned product"
            className="rounded-lg border max-h-48 object-contain mx-auto"
          />
          <div className="grid grid-cols-3 gap-3 mt-4 text-xs">
            <div><div className="text-gray-400">OCR Confidence</div><div className="font-semibold">{inspection.ocr_confidence}%</div></div>
            <div><div className="text-gray-400">Readability</div><div className="font-semibold">{inspection.readability_status}</div></div>
            <div><div className="text-gray-400">Label Side</div><div className="font-semibold capitalize">{inspection.image_label}</div></div>
          </div>
        </div>
      </div>

      <div className="card mb-6">
        <h3 className="font-semibold text-gray-700 mb-3">Extracted Declarations</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {Object.entries(FIELD_LABELS).map(([key, lbl]) => (
            <div key={key}>
              <div className="text-xs text-gray-400">{lbl}</div>
              <div className="font-medium text-gray-800">{declarations?.[key] || <span className="text-gray-300">—</span>}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-700 mb-3">Violation Details / Compliance Check Results</h3>
        <div className="space-y-3">
          {violations.map(v => (
            <div key={v.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-1">
                <div className="font-semibold text-gray-800 text-sm">{v.rule_title}</div>
                <StatusBadge status={v.result} />
              </div>
              <p className="text-sm text-gray-600">{v.explanation}</p>
              <div className="text-xs text-gray-400 mt-2 grid grid-cols-1 md:grid-cols-3 gap-2">
                <div><span className="font-semibold text-gray-500">Evidence:</span> {v.evidence}</div>
                <div><span className="font-semibold text-gray-500">Legal Reference:</span> {v.legal_reference}</div>
                <div><span className="font-semibold text-gray-500">Recommended Action:</span> {v.recommended_action}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="text-xs text-gray-400 mt-6 border-t pt-4">
        This system provides AI-assisted compliance screening only and does not make a final legal determination.
        All flagged issues must be verified by an authorized Legal Metrology enforcement officer.
      </div>
    </div>
  )
}
