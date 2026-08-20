export type BackendStatus = "waiting" | "online" | "offline"

export type HealthResponse = {
  status: string
}