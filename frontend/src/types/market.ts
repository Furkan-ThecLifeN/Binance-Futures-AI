export type BackendStatus =
  | "loading"
  | "online"
  | "degraded"
  | "offline"


export interface HealthResponse {
  status: "ok" | "degraded"
  service: string
  version: string
  environment: string
  timestamp: string

  dependencies: {
    database: "ok" | "error"
    redis: "ok" | "error"
  }
}