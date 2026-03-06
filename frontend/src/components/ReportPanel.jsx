export default function ReportPanel({ report }) {
  if (!report || Object.keys(report).length === 0) {
    return (
      <div className="report-panel">
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <div className="empty-title">No Report Data</div>
          <div className="empty-sub">Upload a scan with a report or paste text to analyze</div>
        </div>
      </div>
    )
  }

  const { patient_info, findings = [], impression, recommendation, urgency, raw_text } = report

  return (
    <div className="report-panel">
      {/* Patient Info */}
      {patient_info && (
        <div className="info-grid">
          <div className="info-item">
            <div className="info-label">Patient</div>
            <div className="info-value">{patient_info.name || '—'}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Modality</div>
            <div className="info-value">{patient_info.modality || '—'}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Date</div>
            <div className="info-value">{patient_info.date || '—'}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Urgency</div>
            <div className="info-value" style={{ textTransform: 'capitalize' }}>{urgency || '—'}</div>
          </div>
        </div>
      )}

      {/* Urgency banner */}
      {urgency && urgency !== 'routine' && (
        <div className={`urgency-banner urgency-${urgency}`}>
          {urgency === 'critical' ? '🚨' : '⚠️'} {urgency.toUpperCase()} — {
            urgency === 'critical'
              ? 'Immediate attention required'
              : 'Follow-up recommended soon'
          }
        </div>
      )}

      {/* Impression */}
      {impression && (
        <div className="impression-box">
          <div className="impression-label">IMPRESSION</div>
          <div className="impression-text">{impression}</div>
        </div>
      )}

      {/* Findings */}
      {findings.length > 0 && (
        <>
          <p className="panel-title" style={{ marginBottom: 10 }}>
            Findings ({findings.length})
          </p>
          {findings.map((f, i) => (
            <div
              key={i}
              className="finding-card"
              style={{ borderLeftColor: f.color_hex || (f.is_abnormal ? '#ff6d00' : '#00e676') }}
            >
              <div className="finding-organ">
                {f.is_abnormal ? '⚠️' : '✓'} {f.organ}
                {f.location ? ` — ${f.location}` : ''}
              </div>
              <div className="finding-text">{f.finding}</div>
              <div className="finding-meta">
                <span className={`finding-tag severity-${f.severity || 'normal'}`}>
                  {f.severity || 'normal'}
                </span>
                {f.size_cm && (
                  <span className="finding-tag" style={{ background: 'rgba(100,100,200,0.1)', color: '#94a3b8', borderColor: 'rgba(100,100,200,0.3)' }}>
                    {f.size_cm} cm
                  </span>
                )}
              </div>
            </div>
          ))}
        </>
      )}

      {/* Recommendation */}
      {recommendation && (
        <div style={{ marginTop: 12 }}>
          <p className="panel-title">Recommendation</p>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: 12,
            fontSize: 13,
            color: 'var(--text-2)',
            lineHeight: 1.6,
          }}>
            {recommendation}
          </div>
        </div>
      )}

      {/* Raw text fallback */}
      {raw_text && findings.length === 0 && (
        <div style={{ marginTop: 12 }}>
          <p className="panel-title">Raw Report Text</p>
          <pre style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: 12,
            fontSize: 11,
            color: 'var(--text-2)',
            whiteSpace: 'pre-wrap',
            overflowWrap: 'break-word',
          }}>
            {raw_text}
          </pre>
        </div>
      )}
    </div>
  )
}
