import type { HealthResponse } from "@/types/market"


const API_BASE_URL = "http://127.0.0.1:8000"


export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/health`)

  if (!response.ok) {
    throw new Error(
      `Backend health request failed: ${response.status}`,
    )
  }

  return response.json()
}