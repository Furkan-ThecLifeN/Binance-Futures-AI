export interface Candle {
  symbol: string
  interval: string
  open_time: string
  close_time: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  quote_volume: number
  trades: number
  taker_buy_base_volume: number
  taker_buy_quote_volume: number
}

export interface CandleResponse {
  symbol: string
  interval: string
  count: number
  candles: Candle[]
}

export interface NormalizedLiveEvent {
  event_type: string
  symbol: string
  event_time: string
  received_at: string
  sequence_id: number | null
  data: Record<string, unknown>
}

export interface MarketHealth {
  symbol?: string
  stale?: boolean
  duplicate?: boolean
  missing_candles?: number
  duplicate_events?: number
  stale_events?: number
  orderbook_synced?: boolean
  warnings?: string[]
  errors?: string[]
  updated_at?: string
}

export interface MarketSnapshot {
  symbol: string
  price: number | null
  health: MarketHealth | null
  trade: NormalizedLiveEvent | null
  book_ticker: NormalizedLiveEvent | null
  klines: {
    "1m": NormalizedLiveEvent | null
    "5m": NormalizedLiveEvent | null
    "15m": NormalizedLiveEvent | null
    "1h": NormalizedLiveEvent | null
  }
}

export interface FactorScore {
  long: number
  short: number
  max_score: number
  reasons_long: string[]
  reasons_short: string[]
}

export interface Confluence {
  long_score: number
  short_score: number
  setup_bias:
    | "LONG_BIAS"
    | "SHORT_BIAS"
    | "NO_TRADE"

  score_type: string
  probability: boolean

  factors: Record<
    string,
    FactorScore
  >
}

export interface AnalyticsSnapshot {
  symbol: string
  interval: string

  technical_indicators: {
    close?: number | null
    ema_9?: number | null
    ema_20?: number | null
    ema_50?: number | null
    ema_100?: number | null
    ema_200?: number | null
    rsi_7?: number | null
    rsi_14?: number | null
    atr_14?: number | null
    atr_pct?: number | null
    vwap?: number | null
  }

  market_structure: {
    trend?: string
    event?: string | null
    last_swing_high?: number | null
    last_swing_low?: number | null
    recent_labels?: string[]
  }

  volume_analysis: {
    volume?: number | null
    volume_sma?: number | null
    rvol?: number | null
    volume_change_pct?: number | null
    volume_acceleration?: number | null
  }

  order_flow: {
    buy_volume?: number
    sell_volume?: number
    delta?: number
    cvd?: number
    buy_ratio?: number
    sell_ratio?: number
    trade_velocity_1m?: number
    large_trade_count?: number
  }

  order_book: {
    valid?: boolean
    spread?: number | null
    spread_bps?: number | null
    imbalance?: number | null
    pressure?: string | null
    microprice?: number | null
    synced?: boolean
  }

  derivatives: {
    open_interest?: number | null
    oi_change_pct?: number | null
    funding_rate?: number | null
    funding_bias?: string
    funding_time?: number | null
    price_change_pct?: number | null
    price_oi_relation?: string
  }

  support_resistance: {
    current_price?: number
    supports?: Array<{
      price: number
      strength: number
      distance_pct: number
    }>
    resistances?: Array<{
      price: number
      strength: number
      distance_pct: number
    }>
  }

  volatility: {
    atr?: number | null
    atr_pct?: number | null
    realized_volatility?: number | null
    range_pct?: number | null
    state?: string
  }

  market_regime: {
    regime?: string
    bullish_alignment?: boolean
    bearish_alignment?: boolean
    above_ema_200?: boolean
    below_ema_200?: boolean
  }

  confluence: Confluence
}

export interface MarketWebSocketMessage {
  type: "market_update"
  symbol: string
  data: MarketSnapshot
}