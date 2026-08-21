export type BackendStatus =
  | "loading"
  | "online"
  | "offline"


export interface HealthResponse {
  status: string
  service: string
  version: string
  environment: string
  timestamp: string
}