import type {
  AnalyticsSnapshot,
  CandleResponse,
  MarketSnapshot,
} from "../types/market"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000/api"

async function fetchJson<T>(
  path: string,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
  )

  if (!response.ok) {
    const text =
      await response.text()

    throw new Error(
      `API ${response.status}: ${text}`,
    )
  }

  return response.json() as Promise<T>
}

export function getMarket(
  symbol: string,
): Promise<MarketSnapshot> {
  return fetchJson(
    `/market/${symbol.toUpperCase()}`,
  )
}

export function getCandles(
  symbol: string,
  interval = "5m",
  limit = 300,
): Promise<CandleResponse> {
  return fetchJson(
    `/market/${symbol.toUpperCase()}/candles` +
      `?interval=${encodeURIComponent(interval)}` +
      `&limit=${limit}`,
  )
}

export function getDerivatives(
  symbol: string,
) {
  return fetchJson<
    AnalyticsSnapshot["derivatives"]
  >(
    `/market/${symbol.toUpperCase()}/derivatives`,
  )
}

export function getAnalytics(
  symbol: string,
  interval = "5m",
): Promise<AnalyticsSnapshot> {
  return fetchJson(
    `/analytics/${symbol.toUpperCase()}` +
      `?interval=${encodeURIComponent(interval)}`,
  )
}

export interface BackendHealth {
  status: "ok" | "degraded" | "error"
  app?: string
  version?: string
  environment?: string

  dependencies: {
    database: string
    redis: string
  }
}

export function getBackendHealth(): Promise<BackendHealth> {
  return fetchJson<BackendHealth>("/health")
}