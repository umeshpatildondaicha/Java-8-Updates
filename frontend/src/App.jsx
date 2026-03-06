import { useState, useCallback } from 'react'
import UploadZone from './components/UploadZone.jsx'
import JobStatus from './components/JobStatus.jsx'
import Viewer3D from './components/Viewer3D.jsx'
import ReportPanel from './components/ReportPanel.jsx'
import StructureList from './components/StructureList.jsx'
import { uploadFile, uploadReportText, pollJob } from './services/api.js'

const TABS = ['3D View', 'MPR Slices', 'Report', 'X-Ray']

export default function App() {
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('3D View')
  const [error, setError] = useState('')

  const result = job?.result || {}

  const handleUpload = useCallback(async (file, reportText) => {
    setLoading(true)
    setError('')
    setJob(null)

    try {
      let data
      if (file) {
        data = await uploadFile(file, reportText)
      } else {
        data = await uploadReportText(reportText)
      }

      // Initial job state
      setJob({ job_id: data.job_id, status: 'queued', progress: 0, message: 'Queued...' })

      // Auto-select best tab when done
      const stop = pollJob(data.job_id, (updatedJob) => {
        setJob(updatedJob)
        if (updatedJob.status === 'completed') {
          const r = updatedJob.result || {}
          if (r.type === '3d')     setActiveTab('3D View')
          if (r.type === '2d')     setActiveTab('X-Ray')
          if (r.type === 'report') setActiveTab('Report')
          setLoading(false)
          stop()
        }
        if (updatedJob.status === 'failed') {
          setLoading(false)
          stop()
        }
      })

    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed')
      setLoading(false)
    }
  }, [])

  const has3D     = result.type === '3d' && result.meshes?.length > 0
  const hasPreviews = result.type === '3d' && result.previews
  const hasImage  = result.type === '2d' && result.image_url
  const hasReport = result.report && Object.keys(result.report).length > 0

  const visibleTabs = [
    has3D     && '3D View',
    hasPreviews && 'MPR Slices',
    hasReport && 'Report',
    hasImage  && 'X-Ray',
  ].filter(Boolean)

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <span style={{ fontSize: 22 }}>🫁</span>
        <div>
          <div className="header-logo">MedViz3D</div>
          <div className="header-sub">AI Medical Imaging Platform</div>
        </div>
        <span className="header-badge">Powered by Claude AI + MedSAM</span>
      </header>

      {/* Main Workspace */}
      <div className="workspace">
        {/* ── Sidebar ─────────────────────────────────── */}
        <aside className="sidebar">
          <UploadZone onUpload={handleUpload} loading={loading} />

          {error && (
            <div className="panel">
              <p style={{ color: 'var(--red)', fontSize: 13 }}>❌ {error}</p>
            </div>
          )}

          {job && <JobStatus job={job} />}

          {has3D && (
            <StructureList
              meshes={result.meshes}
              onVisibilityChange={(name, visible) => {
                // Niivue mesh visibility is controlled through reload; managed via state
                console.log('visibility', name, visible)
              }}
              onOpacityChange={(name, opacity) => {
                console.log('opacity', name, opacity)
              }}
            />
          )}
        </aside>

        {/* ── Main Viewer ──────────────────────────────── */}
        <main className="viewer-area">
          {/* Tabs */}
          {visibleTabs.length > 0 && (
            <div className="viewer-tabs">
              {visibleTabs.map((tab) => (
                <button
                  key={tab}
                  className={`viewer-tab ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab === '3D View'    && '🧬 '}
                  {tab === 'MPR Slices' && '🔬 '}
                  {tab === 'Report'     && '📋 '}
                  {tab === 'X-Ray'      && '📸 '}
                  {tab}
                </button>
              ))}
            </div>
          )}

          <div className="viewer-content">
            {/* Loading state */}
            {loading && job?.status === 'processing' && (
              <div className="empty-state">
                <div className="spinner" />
                <div className="empty-title">{job.message || 'Processing...'}</div>
                <div className="empty-sub">{job.progress}% complete</div>
              </div>
            )}

            {/* Empty state */}
            {!loading && !job && (
              <div className="empty-state">
                <div className="empty-icon">🏥</div>
                <div className="empty-title">Upload a medical file to begin</div>
                <div className="empty-sub">
                  CT scans · MRI · X-rays · Radiology reports
                </div>
              </div>
            )}

            {/* 3D View */}
            {activeTab === '3D View' && has3D && (
              <Viewer3D
                key={`3d-${job.job_id}`}
                volumeUrl={result.volume_url}
                meshes={result.meshes}
                viewMode="3d"
              />
            )}

            {/* MPR Slices */}
            {activeTab === 'MPR Slices' && hasPreviews && (
              <Viewer3D
                key={`mpr-${job.job_id}`}
                volumeUrl={result.volume_url}
                meshes={result.meshes}
                viewMode="mpr"
              />
            )}

            {/* Report */}
            {activeTab === 'Report' && (
              <ReportPanel report={result.report} />
            )}

            {/* X-Ray */}
            {activeTab === 'X-Ray' && hasImage && (
              <div className="image-viewer">
                <img src={result.image_url} alt="Medical scan" />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
