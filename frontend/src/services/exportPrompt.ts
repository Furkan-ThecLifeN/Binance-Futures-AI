import type {
  AnalyticsSnapshot,
  MarketSnapshot,
} from "../types/market"


function prettyValue(
  value: unknown,
): string {
  if (
    value === null
    || value === undefined
  ) {
    return "Yok"
  }

  if (
    typeof value === "number"
  ) {
    return Number.isFinite(value)
      ? value.toString()
      : "Yok"
  }

  if (
    typeof value === "boolean"
  ) {
    return value
      ? "Evet"
      : "Hayır"
  }

  if (
    typeof value === "string"
  ) {
    return value
  }

  return JSON.stringify(
    value,
    null,
    2,
  )
}


export function buildAnalysisPrompt(
  market: MarketSnapshot,
  analytics: AnalyticsSnapshot,
): string {
  const indicators =
    analytics.technical_indicators

  const structure =
    analytics.market_structure

  const volume =
    analytics.volume_analysis

  const orderFlow =
    analytics.order_flow

  const orderBook =
    analytics.order_book

  const derivatives =
    analytics.derivatives

  const levels =
    analytics.support_resistance

  const volatility =
    analytics.volatility

  const regime =
    analytics.market_regime

  const confluence =
    analytics.confluence

  const health =
    market.health


  return `
BINANCE FUTURES AI MARKET INTELLIGENCE
======================================

ANALİZ ZAMANI
${new Date().toISOString()}

SEMBOL
${market.symbol}

ANA TIMEFRAME
${analytics.interval}

==================================================
1. CANLI PİYASA
==================================================

Fiyat:
${prettyValue(market.price)}

Son veri tipi:
${prettyValue(
  health?.symbol
    ? market.health
    : null
)}

==================================================
2. DATA QUALITY
==================================================

Stale:
${prettyValue(health?.stale)}

Duplicate:
${prettyValue(health?.duplicate)}

Missing Candles:
${prettyValue(
  health?.missing_candles
)}

Order Book Synced:
${prettyValue(
  health?.orderbook_synced
)}

Warnings:
${prettyValue(
  health?.warnings
)}

Errors:
${prettyValue(
  health?.errors
)}

==================================================
3. TEKNİK İNDİKATÖRLER
==================================================

Close:
${prettyValue(indicators.close)}

EMA 9:
${prettyValue(indicators.ema_9)}

EMA 20:
${prettyValue(indicators.ema_20)}

EMA 50:
${prettyValue(indicators.ema_50)}

EMA 100:
${prettyValue(indicators.ema_100)}

EMA 200:
${prettyValue(indicators.ema_200)}

RSI 7:
${prettyValue(indicators.rsi_7)}

RSI 14:
${prettyValue(indicators.rsi_14)}

ATR 14:
${prettyValue(indicators.atr_14)}

ATR %:
${prettyValue(indicators.atr_pct)}

VWAP:
${prettyValue(indicators.vwap)}

==================================================
4. MARKET STRUCTURE
==================================================

Trend:
${prettyValue(structure.trend)}

Son Structure Event:
${prettyValue(structure.event)}

Son Swing High:
${prettyValue(
  structure.last_swing_high
)}

Son Swing Low:
${prettyValue(
  structure.last_swing_low
)}

Son Yapı Etiketleri:
${prettyValue(
  structure.recent_labels
)}

==================================================
5. VOLUME
==================================================

Volume:
${prettyValue(volume.volume)}

Volume SMA:
${prettyValue(volume.volume_sma)}

RVOL:
${prettyValue(volume.rvol)}

Volume Change %:
${prettyValue(
  volume.volume_change_pct
)}

Volume Acceleration:
${prettyValue(
  volume.volume_acceleration
)}

==================================================
6. ORDER FLOW
==================================================

Buy Volume:
${prettyValue(
  orderFlow.buy_volume
)}

Sell Volume:
${prettyValue(
  orderFlow.sell_volume
)}

Delta:
${prettyValue(orderFlow.delta)}

CVD:
${prettyValue(orderFlow.cvd)}

Buy Ratio:
${prettyValue(
  orderFlow.buy_ratio
)}

Sell Ratio:
${prettyValue(
  orderFlow.sell_ratio
)}

Trade Velocity 1m:
${prettyValue(
  orderFlow.trade_velocity_1m
)}

Large Trade Count:
${prettyValue(
  orderFlow.large_trade_count
)}

==================================================
7. ORDER BOOK
==================================================

Valid:
${prettyValue(orderBook.valid)}

Synced:
${prettyValue(orderBook.synced)}

Spread:
${prettyValue(orderBook.spread)}

Spread BPS:
${prettyValue(
  orderBook.spread_bps
)}

Imbalance:
${prettyValue(
  orderBook.imbalance
)}

Pressure:
${prettyValue(
  orderBook.pressure
)}

Microprice:
${prettyValue(
  orderBook.microprice
)}

==================================================
8. DERIVATIVES
==================================================

Open Interest:
${prettyValue(
  derivatives.open_interest
)}

OI Change %:
${prettyValue(
  derivatives.oi_change_pct
)}

Funding Rate:
${prettyValue(
  derivatives.funding_rate
)}

Funding Bias:
${prettyValue(
  derivatives.funding_bias
)}

Price Change %:
${prettyValue(
  derivatives.price_change_pct
)}

Price / OI Relation:
${prettyValue(
  derivatives.price_oi_relation
)}

==================================================
9. SUPPORT / RESISTANCE
==================================================

Mevcut Fiyat:
${prettyValue(
  levels.current_price
)}

Supports:
${prettyValue(levels.supports)}

Resistances:
${prettyValue(
  levels.resistances
)}

==================================================
10. VOLATILITY
==================================================

ATR:
${prettyValue(volatility.atr)}

ATR %:
${prettyValue(
  volatility.atr_pct
)}

Realized Volatility:
${prettyValue(
  volatility.realized_volatility
)}

Range %:
${prettyValue(
  volatility.range_pct
)}

Volatility State:
${prettyValue(
  volatility.state
)}

==================================================
11. MARKET REGIME
==================================================

Regime:
${prettyValue(regime.regime)}

Bullish Alignment:
${prettyValue(
  regime.bullish_alignment
)}

Bearish Alignment:
${prettyValue(
  regime.bearish_alignment
)}

Price Above EMA200:
${prettyValue(
  regime.above_ema_200
)}

Price Below EMA200:
${prettyValue(
  regime.below_ema_200
)}

==================================================
12. DETERMINISTIC CONFLUENCE
==================================================

LONG SCORE:
${prettyValue(
  confluence.long_score
)} / 100

SHORT SCORE:
${prettyValue(
  confluence.short_score
)} / 100

SETUP BIAS:
${prettyValue(
  confluence.setup_bias
)}

SCORE TYPE:
${prettyValue(
  confluence.score_type
)}

Bu skor kazanma olasılığı değildir.

Alt Faktörler:
${JSON.stringify(
  confluence.factors,
  null,
  2,
)}

==================================================
CHATGPT ANALİZ TALİMATI
==================================================

Yukarıdaki Binance Futures piyasa verilerini birlikte analiz et.

Öncelik sırası:

1. Data quality kontrolü yap.
2. Ana trend ve market structure yönünü belirle.
3. EMA, RSI, ATR ve VWAP momentumunu değerlendir.
4. Volume ve RVOL teyidini kontrol et.
5. Order flow içindeki delta, CVD ve agresif alım/satım dengesini değerlendir.
6. Order book imbalance, spread ve pressure verilerini değerlendir.
7. Open Interest ve funding ilişkisini yorumla.
8. Support/resistance seviyelerinin mevcut fiyata uzaklığını değerlendir.
9. Volatility ve market regime koşullarını yorumla.
10. Deterministic LONG/SHORT skorlarını yalnız yardımcı setup uyumu olarak kullan.

Sonucu şu formatta ver:

MARKET REGIME:
TREND:
STRUCTURE:
MOMENTUM:
VOLUME:
ORDER FLOW:
ORDER BOOK:
DERIVATIVES:
SUPPORT / RESISTANCE:
VOLATILITY:

BULLISH ARGUMENTS:
- ...

BEARISH ARGUMENTS:
- ...

CRITICAL SUPPORT:
...

CRITICAL RESISTANCE:
...

INVALIDATION:
...

FINAL BIAS:
LONG BIAS / SHORT BIAS / NO TRADE

CONFLUENCE DEĞERLENDİRMESİ:
...

RİSKLER:
...

Kararı yalnız tek bir indikatöre göre verme.
Çelişkili sinyaller varsa açıkça belirt.
Data quality bozuksa bunu en başta belirt.
NO TRADE sonucunu normal bir sonuç olarak kabul et.
`.trim()
}


export function downloadPromptFile(
  symbol: string,
  content: string,
): void {
  const blob = new Blob(
    [
      content,
    ],
    {
      type:
        "text/plain;charset=utf-8",
    },
  )

  const url =
    URL.createObjectURL(
      blob,
    )

  const link =
    document.createElement(
      "a",
    )

  const timestamp =
    new Date()
      .toISOString()
      .replaceAll(
        ":",
        "-",
      )
      .replace(
        "T",
        "_",
      )
      .slice(
        0,
        19,
      )

  link.href = url

  link.download =
    `${symbol}_AI_ANALYSIS_${timestamp}.txt`

  document.body.appendChild(
    link,
  )

  link.click()

  document.body.removeChild(
    link,
  )

  URL.revokeObjectURL(
    url,
  )
}