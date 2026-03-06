import axios from 'axios'

const api = axios.create({ baseURL: '' })

export async function uploadFile(file, reportText = '') {
  const form = new FormData()
  form.append('file', file)
  if (reportText) form.append('report_text', reportText)

  const res = await api.post('/api/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function uploadReportText(text) {
  const form = new FormData()
  form.append('report_text', text)
  const res = await api.post('/api/upload/report-text', form)
  return res.data
}

export async function getJobStatus(jobId) {
  const res = await api.get(`/api/jobs/${jobId}`)
  return res.data
}

export async function parseReportText(text) {
  const res = await api.post('/api/reports/parse', { text })
  return res.data
}

export function pollJob(jobId, onUpdate, intervalMs = 2000) {
  const handle = setInterval(async () => {
    try {
      const job = await getJobStatus(jobId)
      onUpdate(job)
      if (job.status === 'completed' || job.status === 'failed') {
        clearInterval(handle)
      }
    } catch (err) {
      console.error('Poll error:', err)
    }
  }, intervalMs)
  return () => clearInterval(handle)
}
