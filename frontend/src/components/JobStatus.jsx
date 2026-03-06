export default function JobStatus({ job }) {
  if (!job) return null

  const statusClass = `status-badge status-${job.status}`
  const statusEmoji = {
    queued: '⏳',
    processing: '⚙️',
    completed: '✅',
    failed: '❌',
  }[job.status] || '•'

  return (
    <div className="panel">
      <p className="panel-title">Processing Status</p>

      <div style={{ marginBottom: 10 }}>
        <span className={statusClass}>
          {statusEmoji} {job.status.toUpperCase()}
        </span>
      </div>

      {job.status === 'processing' && (
        <>
          <div className="progress-bar-wrap">
            <div
              className="progress-bar-fill"
              style={{ width: `${job.progress}%` }}
            />
          </div>
          <p className="progress-msg">{job.message || 'Processing...'}</p>
        </>
      )}

      {job.status === 'failed' && (
        <p style={{ fontSize: 12, color: 'var(--red)', marginTop: 6 }}>
          {job.error || 'An error occurred'}
        </p>
      )}

      {job.status === 'completed' && job.result && (
        <div style={{ marginTop: 8 }}>
          {job.result.type === '3d' && (
            <p className="progress-msg">
              🧬 {job.result.structure_count || 0} structures segmented
            </p>
          )}
          {job.result.type === '2d' && (
            <p className="progress-msg">🔬 X-ray analyzed with AI</p>
          )}
          {job.result.type === 'report' && (
            <p className="progress-msg">📋 Report parsed</p>
          )}
        </div>
      )}

      {job.job_id && (
        <p style={{ fontSize: 10, color: 'var(--text-3)', marginTop: 8 }}>
          Job ID: {job.job_id.slice(0, 8)}...
        </p>
      )}
    </div>
  )
}
