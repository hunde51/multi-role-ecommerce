type BackendResponse = {
  message: string
}

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

async function getBackend(): Promise<BackendResponse> {
  const response = await fetch(`${API_BASE_URL}/`)
  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`)
  }
  return response.json()
}

export async function getBackendMessage(): Promise<string> {
  try {
    const data = await getBackend()
    return data.message
  } catch {
    return 'Could not connect to backend.'
  }
}
