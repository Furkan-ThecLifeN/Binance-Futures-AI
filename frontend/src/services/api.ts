import type { HealthResponse } from "@/types/market"


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000"


export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/health`,
  )

  const data: HealthResponse =
    await response.json()

  if (
    response.status !== 200 &&
    response.status !== 503
  ) {
    throw new Error(
      `Backend health request failed: ${response.status}`,
    )
  }

  return data
}