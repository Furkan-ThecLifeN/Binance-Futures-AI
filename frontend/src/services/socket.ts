import type {
  MarketWebSocketMessage,
} from "../types/market"


export type MarketMessageHandler = (
  message: MarketWebSocketMessage,
) => void


export type MarketSocketStatusHandler = (
  connected: boolean,
) => void


export function connectMarketSocket(
  symbol: string,
  onMessage: MarketMessageHandler,
  onStatus?: MarketSocketStatusHandler,
): () => void {
  let socket: WebSocket | null =
    null

  let reconnectTimer:
    | number
    | null = null

  let manuallyClosed =
    false


  const getWebSocketUrl =
    () => {
      const protocol =
        window.location.protocol
        === "https:"
          ? "wss:"
          : "ws:"

      const backendHost =
        window.location.hostname

      return (
        `${protocol}//` +
        `${backendHost}:8000` +
        `/ws/market/` +
        `${symbol.toUpperCase()}`
      )
    }


  const connect =
    () => {
      const url =
        getWebSocketUrl()

      console.log(
        "Connecting market WS:",
        url,
      )

      socket =
        new WebSocket(
          url,
        )


      socket.onopen =
        () => {
          console.log(
            "Market WebSocket connected",
          )

          onStatus?.(
            true,
          )
        }


      socket.onmessage =
        (event) => {
          try {
            const message =
              JSON.parse(
                event.data,
              ) as MarketWebSocketMessage

            onMessage(
              message,
            )

          } catch (error) {
            console.error(
              "Invalid market WebSocket message",
              error,
            )
          }
        }


      socket.onerror =
        (event) => {
          console.error(
            "Market WebSocket error",
            event,
          )

          onStatus?.(
            false,
          )
        }


      socket.onclose =
        () => {
          onStatus?.(
            false,
          )

          if (
            manuallyClosed
          ) {
            return
          }

          reconnectTimer =
            window.setTimeout(
              () => {
                connect()
              },
              3000,
            )
        }
    }


  connect()


  return () => {
    manuallyClosed =
      true

    if (
      reconnectTimer !== null
    ) {
      window.clearTimeout(
        reconnectTimer,
      )
    }

    socket?.close()
  }
}