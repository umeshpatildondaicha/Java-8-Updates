import { useRef, useState } from 'react'

export default function UploadZone({ onUpload, loading }) {
  const inputRef = useRef(null)
  const [drag, setDrag] = useState(false)
  const [reportText, setReportText] = useState('')

  const handle = (file) => {
    if (!file) return
    onUpload(file, reportText)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDrag(false)
    const file = e.dataTransfer.files[0]
    handle(file)
  }

  return (
    <div className="panel">
      <p className="panel-title">Upload Medical File</p>

      <div
        className={`upload-zone ${drag ? 'drag-over' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
      >
        <div className="upload-icon">🏥</div>
        <div className="upload-title">Drop file or click to browse</div>
        <div className="upload-sub">CT, MRI, X-Ray, Blood report, PDF</div>
        <div className="upload-types">
          {['DICOM', 'NIfTI', 'ZIP', 'PNG/JPG', 'PDF', 'TXT'].map(t => (
            <span key={t} className="type-tag">{t}</span>
          ))}
        </div>
        <input
          ref={inputRef}
          type="file"
          style={{ display: 'none' }}
          accept=".dcm,.nii,.gz,.png,.jpg,.jpeg,.pdf,.txt,.zip"
          onChange={(e) => handle(e.target.files[0])}
        />
      </div>

      <div style={{ marginTop: 12 }}>
        <p style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 6 }}>
          Attach radiology report text (optional)
        </p>
        <textarea
          className="report-input"
          placeholder="Paste radiology report here... (FINDINGS: There is a prominent mass...)"
          value={reportText}
          onChange={(e) => setReportText(e.target.value)}
        />
      </div>

      <button
        className="btn btn-secondary"
        style={{ marginTop: 4 }}
        onClick={() => {
          if (reportText.trim().length > 20) {
            onUpload(null, reportText)
          } else {
            alert('Enter at least 20 characters of report text')
          }
        }}
        disabled={loading}
      >
        📄 Parse Report Text Only
      </button>
    </div>
  )
}
