const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  get: (path) => fetch(`${API}${path}`).then(r => r.json()),
  post: (path, body) =>
    fetch(`${API}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then(r => r.json()),
  upload: (path, formData) =>
    fetch(`${API}${path}`, { method: 'POST', body: formData }).then(r => r.json()),
}

export const audioUrl = (path) => `${API}${path}`
