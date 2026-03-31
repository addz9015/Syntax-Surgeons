export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8010').replace(/\/$/, '')

export async function apiGet(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json()
}

export async function apiPost(path, body) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const message = await response.text()
    throw new Error(`${response.status} ${response.statusText}: ${message}`)
  }
  return response.json()
}
