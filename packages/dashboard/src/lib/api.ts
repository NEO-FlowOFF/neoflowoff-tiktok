const defaultApiBaseUrl = 'https://neo-tiktok-api.up.railway.app'

export const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || defaultApiBaseUrl

export async function fetchApiHealth(signal?: AbortSignal) {
  const response = await fetch(`${apiBaseUrl}/health`, {
    headers: {
      Accept: 'application/json',
    },
    signal,
  })

  if (!response.ok) {
    throw new Error(`API healthcheck failed with status ${response.status}`)
  }

  return response.json() as Promise<{ ok: boolean }>
}
