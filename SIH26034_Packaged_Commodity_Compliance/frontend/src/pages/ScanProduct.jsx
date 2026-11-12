import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { errorMessage } from '../api'

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

const DEMO_PRODUCTS = [
  { id: 1, name: 'Demo Product 1', hint: 'Mostly Compliant', color: 'bg-green-50 border-green-200 text-green-700' },
  { id: 2, name: 'Demo Product 2', hint: 'Missing Declaration', color: 'bg-yellow-50 border-yellow-200 text-yellow-700' },
  { id: 3, name: 'Demo Product 3', hint: 'Readability Issue', color: 'bg-blue-50 border-blue-200 text-blue-700' },
]

export default function ScanProduct() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)

  const [previewUrl, setPreviewUrl] = useState(null)
  const [label, setLabel] = useState('front')
  const [loadingOcr, setLoadingOcr] = useState(false)
  const [ocrResult, setOcrResult] = useState(null) // full response from upload/demo endpoint
  const [fields, setFields] = useState(null)
  const [error, setError] = useState('')
  const [analyzing, setAnalyzing] = useState(false)

  const reset = () => {
    setPreviewUrl(null)
    setOcrResult(null)
    setFields(null)
    setError('')
  }

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setError('')
    setPreviewUrl(URL.createObjectURL(file))
    setOcrResult(null)
    setFields(null)
    setLoadingOcr(true)
    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('label', label)
      const res = await api.post('/scan/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setOcrResult(res.data)
      setFields(res.data.declarations)
    } catch (err) {
      setError(errorMessage(err, 'OCR processing failed.'))
    } finally {
      setLoadingOcr(false)
    }
  }

  const handleScanDemo = async (demoId) => {
    reset()
    setLoadingOcr(true)
    try {
      const res = await api.post(`/scan/demo/${demoId}`)
      setOcrResult(res.data)
      setFields(res.data.declarations)
      setPreviewUrl(`/api/scan/demo-image/${demoId}`)
    } catch (err) {
      setError(errorMessage(err, 'Demo scan failed.'))
    } finally {
      setLoadingOcr(false)
    }
  }

  const handleFieldChange = (key, value) => {
    setFields(prev => ({ ...prev, [key]: value }))
  }

  const handleAnalyze = async () => {
    setAnalyzing(true)
    setError('')
    try {
      const payload = {
        image_filename: ocrResult.image_filename,
        image_label: ocrResult.image_label,
        is_demo: ocrResult.is_demo,
        ocr_raw_text: ocrResult.ocr_raw_text,
        ocr_confidence: ocrResult.ocr_confidence,
        readability_status: ocrResult.readability_status,
        declarations: fields,
      }
      const res = await api.post('/scan/analyze', payload)
      navigate(`/inspections/${res.data.inspection_id}`)
    } catch (err) {
      setError(errorMessage(err, 'Compliance analysis failed.'))
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-navy-900 mb-1">Scan Product</h1>
      <p className="text-gray-500 text-sm mb-6">Upload a label image or run one of the demo/synthetic products to test the pipeline.</p>

      {error && (
        <div className="mb-4 text-sm bg-red-50 border border-red-200 text-red-700 rounded-lg px-3 py-2">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-3">1. Upload Label Image</h3>
          <div className="mb-3">
            <label className="label-text">Image Side</label>
            <select className="input-field" value={label} onChange={e => setLabel(e.target.value)}>
              <option value="front">Front</option>
              <option value="back">Back</option>
              <option value="side">Side</option>
            </select>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png, image/jpeg"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-600 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-navy-800 file:text-white file:text-sm file:font-medium hover:file:bg-navy-700"
          />

          <div className="mt-5 pt-4 border-t border-gray-100">
            <div className="text-xs text-gray-500 mb-2 font-semibold uppercase tracking-wide">
              Or Run a Demo / Synthetic Product
            </div>
            <div className="grid grid-cols-3 gap-2">
              {DEMO_PRODUCTS.map(d => (
                <button key={d.id} onClick={() => handleScanDemo(d.id)}
                  className={`border rounded-lg px-2 py-3 text-xs font-semibold text-center ${d.color} hover:opacity-80`}>
                  {d.name}
                  <div className="text-[10px] font-normal mt-0.5">{d.hint}</div>
                </button>
              ))}
            </div>
          </div>

          {previewUrl && (
            <div className="mt-5">
              <div className="text-xs text-gray-500 mb-2 font-semibold uppercase tracking-wide">Preview</div>
              <img src={previewUrl} alt="preview" className="rounded-lg border max-h-64 object-contain" />
            </div>
          )}

          {loadingOcr && <div className="mt-4 text-sm text-navy-700 font-medium">Running OCR… please wait.</div>}
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-3">2. OCR Result & Extracted Declarations</h3>
          {!ocrResult && <div className="text-sm text-gray-400 py-10 text-center">Upload or scan a demo product to see OCR results here.</div>}

          {ocrResult && (
            <>
              <div className="mb-3 flex gap-4 text-xs">
                <div><span className="text-gray-400">OCR Confidence:</span> <span className="font-semibold">{ocrResult.ocr_confidence}%</span></div>
                <div><span className="text-gray-400">Readability:</span> <span className="font-semibold">{ocrResult.readability_status}</span></div>
                <div><span className="text-gray-400">Words Detected:</span> <span className="font-semibold">{ocrResult.word_count}</span></div>
              </div>

              <details className="mb-4">
                <summary className="text-xs text-navy-700 cursor-pointer font-semibold">View raw OCR text</summary>
                <pre className="mt-2 text-[11px] bg-gray-50 border rounded-lg p-3 whitespace-pre-wrap max-h-32 overflow-y-auto">{ocrResult.ocr_raw_text || '(no text detected)'}</pre>
              </details>

              <div className="text-xs text-gray-500 mb-2 font-semibold uppercase tracking-wide">
                Review / Edit Extracted Fields
              </div>
              <div className="space-y-3 mb-5">
                {Object.entries(FIELD_LABELS).map(([key, lbl]) => (
                  <div key={key}>
                    <label className="label-text">{lbl}</label>
                    <input
                      className="input-field"
                      value={fields[key] || ''}
                      onChange={e => handleFieldChange(key, e.target.value)}
                      placeholder="(not detected — edit if visible on label)"
                    />
                  </div>
                ))}
              </div>

              <button onClick={handleAnalyze} disabled={analyzing} className="btn-primary w-full justify-center flex">
                {analyzing ? 'Running Compliance Analysis…' : 'Run Compliance Analysis'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
