import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  useQuery,
} from "@tanstack/react-query"

import {
  getAnalytics,
  getMarket,
} from "../services/api"

import {
  buildAnalysisPrompt,
  downloadPromptFile,
} from "../services/exportPrompt"

import {
  connectMarketSocket,
} from "../services/socket"

import type {
  MarketSnapshot,
} from "../types/market"


const SYMBOL = "BTCUSDT"
const INTERVAL = "5m"


function formatNumber(
  value:
    | number
    | null
    | undefined,

  digits = 2,
): string {
  if (
    value === null
    || value === undefined
    || !Number.isFinite(value)
  ) {
    return "—"
  }

  return value.toLocaleString(
    "en-US",
    {
      maximumFractionDigits:
        digits,
    },
  )
}


function formatPercent(
  value:
    | number
    | null
    | undefined,

  digits = 3,
): string {
  if (
    value === null
    || value === undefined
    || !Number.isFinite(value)
  ) {
    return "—"
  }

  return `${value.toFixed(
    digits,
  )}%`
}


function DataCard({
  title,
  value,
  subtitle,
  valueClassName = "",
}: {
  title: string
  value: string
  subtitle?: string
  valueClassName?: string
}) {
  return (
    <div
      className="
        rounded-xl
        border
        border-neutral-800
        bg-neutral-950
        p-5
      "
    >
      <div
        className="
          text-xs
          font-medium
          uppercase
          tracking-widest
          text-neutral-500
        "
      >
        {title}
      </div>

      <div
        className={`
          mt-3
          break-words
          text-xl
          font-semibold
          text-white
          ${valueClassName}
        `}
      >
        {value}
      </div>

      {subtitle && (
        <div
          className="
            mt-2
            text-xs
            text-neutral-600
          "
        >
          {subtitle}
        </div>
      )}
    </div>
  )
}


function Section({
  title,
  children,
}: {
  title: string
  children:
    React.ReactNode
}) {
  return (
    <section
      className="
        rounded-2xl
        border
        border-neutral-900
        bg-[#050505]
        p-5
      "
    >
      <h2
        className="
          mb-5
          text-sm
          font-semibold
          uppercase
          tracking-widest
          text-neutral-400
        "
      >
        {title}
      </h2>

      {children}
    </section>
  )
}


export default function SymbolPage() {
  const [
    liveMarket,
    setLiveMarket,
  ] = useState<
    MarketSnapshot | null
  >(null)

  const [
    socketConnected,
    setSocketConnected,
  ] = useState(
    false,
  )


  // ------------------------------------------------
  // REST MARKET:
  // yalnız ilk açılışta fallback
  // ------------------------------------------------

  const marketQuery =
    useQuery({
      queryKey: [
        "market",
        SYMBOL,
      ],

      queryFn: () =>
        getMarket(
          SYMBOL,
        ),

      refetchInterval:
        false,

      refetchOnWindowFocus:
        false,

      refetchOnReconnect:
        false,

      staleTime:
        Infinity,

      retry:
        1,
    })


  // ------------------------------------------------
  // ANALYTICS:
  // OTOMATİK REFRESH YOK.
  //
  // Sadece:
  // - sayfa ilk açıldığında
  // - kullanıcı butona bastığında
  // ------------------------------------------------

  const analyticsQuery =
    useQuery({
      queryKey: [
        "analytics",
        SYMBOL,
        INTERVAL,
      ],

      queryFn: () =>
        getAnalytics(
          SYMBOL,
          INTERVAL,
        ),

      refetchInterval:
        false,

      refetchOnWindowFocus:
        false,

      refetchOnReconnect:
        false,

      staleTime:
        Infinity,

      retry:
        1,
    })


  // ------------------------------------------------
  // WEBSOCKET
  //
  // Bu sayfa yenilemesi değildir.
  // Canlı price + health state'i.
  // ------------------------------------------------

  useEffect(() => {
    const disconnect =
      connectMarketSocket(
        SYMBOL,

        (message) => {
          if (
            message.type
            === "market_update"
          ) {
            setLiveMarket(
              message.data,
            )
          }
        },

        (
          connected,
        ) => {
          setSocketConnected(
            connected,
          )
        },
      )

    return () => {
      disconnect()
    }
  }, [])


  const market = (
    liveMarket
    ?? marketQuery.data
    ?? null
  )


  const analytics =
    analyticsQuery.data


  const indicators =
    analytics
      ?.technical_indicators

  const structure =
    analytics
      ?.market_structure

  const volume =
    analytics
      ?.volume_analysis

  const orderFlow =
    analytics
      ?.order_flow

  const orderBook =
    analytics
      ?.order_book

  const derivatives =
    analytics
      ?.derivatives

  const levels =
    analytics
      ?.support_resistance

  const volatility =
    analytics
      ?.volatility

  const regime =
    analytics
      ?.market_regime

  const confluence =
    analytics
      ?.confluence

  const health =
    market?.health


  const biasClass =
    useMemo(
      () => {
        if (
          confluence
            ?.setup_bias
          === "LONG_BIAS"
        ) {
          return (
            "text-emerald-400"
          )
        }

        if (
          confluence
            ?.setup_bias
          === "SHORT_BIAS"
        ) {
          return (
            "text-red-400"
          )
        }

        return (
          "text-amber-400"
        )
      },
      [
        confluence
          ?.setup_bias,
      ],
    )


  const handleRefresh =
    async () => {
      await analyticsQuery.refetch()
    }


  const handleDownload =
    () => {
      if (
        !market
        || !analytics
      ) {
        return
      }

      const prompt =
        buildAnalysisPrompt(
          market,
          analytics,
        )

      downloadPromptFile(
        SYMBOL,
        prompt,
      )
    }


  if (
    !market
    || !analytics
  ) {
    return (
      <main
        className="
          min-h-screen
          bg-[#000000]
          p-8
          text-white
        "
      >
        <div
          className="
            mx-auto
            max-w-7xl
          "
        >
          <div
            className="
              text-lg
              font-semibold
            "
          >
            BTCUSDT verileri hazırlanıyor...
          </div>
        </div>
      </main>
    )
  }


  return (
    <main
      className="
        min-h-screen
        bg-[#000000]
        text-white
      "
    >
      <div
        className="
          mx-auto
          max-w-[1600px]
          p-4
          md:p-7
        "
      >

        {/* HEADER */}

        <header
          className="
            mb-7
            flex
            flex-col
            gap-5
            border-b
            border-neutral-900
            pb-6
            lg:flex-row
            lg:items-end
            lg:justify-between
          "
        >
          <div>
            <div
              className="
                text-xs
                font-medium
                uppercase
                tracking-[0.25em]
                text-neutral-600
              "
            >
              Binance Futures AI
              Market Intelligence
            </div>

            <div
              className="
                mt-2
                flex
                items-end
                gap-5
              "
            >
              <h1
                className="
                  text-4xl
                  font-bold
                  tracking-tight
                "
              >
                BTCUSDT
              </h1>

              <div
                className="
                  pb-1
                  text-3xl
                  font-semibold
                  text-white
                "
              >
                $
                {formatNumber(
                  market.price,
                  2,
                )}
              </div>
            </div>

            <div
              className="
                mt-3
                flex
                items-center
                gap-2
                text-sm
                text-neutral-500
              "
            >
              <span
                className={`
                  h-2
                  w-2
                  rounded-full
                  ${
                    socketConnected
                      ? "bg-emerald-500"
                      : "bg-red-500"
                  }
                `}
              />

              {socketConnected
                ? "Canlı veri bağlı"
                : "Canlı veri bağlantısı yok"}
            </div>
          </div>


          <div
            className="
              flex
              flex-wrap
              gap-3
            "
          >
            <button
              onClick={
                handleRefresh
              }
              disabled={
                analyticsQuery
                  .isFetching
              }
              className="
                rounded-lg
                border
                border-neutral-700
                bg-neutral-950
                px-5
                py-3
                text-sm
                font-semibold
                text-white
                transition
                hover:bg-neutral-900
                disabled:opacity-50
              "
            >
              {analyticsQuery
                .isFetching
                ? "Veriler Güncelleniyor..."
                : "Verileri Yenile"}
            </button>


            <button
              onClick={
                handleDownload
              }
              className="
                rounded-lg
                bg-white
                px-5
                py-3
                text-sm
                font-bold
                text-black
                transition
                hover:bg-neutral-200
              "
            >
              AI Prompt TXT İndir
            </button>
          </div>
        </header>


        {/* CONFLUENCE */}

        <Section
          title="Analiz Özeti"
        >
          <div
            className="
              grid
              gap-4
              sm:grid-cols-2
              lg:grid-cols-5
            "
          >
            <DataCard
              title="Market Regime"
              value={
                regime
                  ?.regime
                ?? "—"
              }
            />

            <DataCard
              title="Trend"
              value={
                structure
                  ?.trend
                ?? "—"
              }
            />

            <DataCard
              title="Setup Bias"
              value={
                confluence
                  ?.setup_bias
                ?? "—"
              }
              valueClassName={
                biasClass
              }
              subtitle={
                "Olasılık değildir"
              }
            />

            <DataCard
              title="Long Score"
              value={
                `${formatNumber(
                  confluence
                    ?.long_score,
                  1,
                )} / 100`
              }
              valueClassName="
                text-emerald-400
              "
            />

            <DataCard
              title="Short Score"
              value={
                `${formatNumber(
                  confluence
                    ?.short_score,
                  1,
                )} / 100`
              }
              valueClassName="
                text-red-400
              "
            />
          </div>
        </Section>


        <div
          className="
            mt-5
            grid
            gap-5
            xl:grid-cols-2
          "
        >

          {/* INDICATORS */}

          <Section
            title="Teknik İndikatörler"
          >
            <div
              className="
                grid
                grid-cols-2
                gap-3
                lg:grid-cols-3
              "
            >
              <DataCard
                title="EMA 9"
                value={
                  formatNumber(
                    indicators
                      ?.ema_9,
                    2,
                  )
                }
              />

              <DataCard
                title="EMA 20"
                value={
                  formatNumber(
                    indicators
                      ?.ema_20,
                    2,
                  )
                }
              />

              <DataCard
                title="EMA 50"
                value={
                  formatNumber(
                    indicators
                      ?.ema_50,
                    2,
                  )
                }
              />

              <DataCard
                title="EMA 100"
                value={
                  formatNumber(
                    indicators
                      ?.ema_100,
                    2,
                  )
                }
              />

              <DataCard
                title="EMA 200"
                value={
                  formatNumber(
                    indicators
                      ?.ema_200,
                    2,
                  )
                }
              />

              <DataCard
                title="VWAP"
                value={
                  formatNumber(
                    indicators
                      ?.vwap,
                    2,
                  )
                }
              />

              <DataCard
                title="RSI 7"
                value={
                  formatNumber(
                    indicators
                      ?.rsi_7,
                    2,
                  )
                }
              />

              <DataCard
                title="RSI 14"
                value={
                  formatNumber(
                    indicators
                      ?.rsi_14,
                    2,
                  )
                }
              />

              <DataCard
                title="ATR 14"
                value={
                  formatNumber(
                    indicators
                      ?.atr_14,
                    2,
                  )
                }
                subtitle={
                  `ATR % ${formatPercent(
                    indicators
                      ?.atr_pct,
                    3,
                  )}`
                }
              />
            </div>
          </Section>


          {/* STRUCTURE */}

          <Section
            title="Market Structure"
          >
            <div
              className="
                grid
                grid-cols-2
                gap-3
              "
            >
              <DataCard
                title="Trend"
                value={
                  structure
                    ?.trend
                  ?? "—"
                }
              />

              <DataCard
                title="Event"
                value={
                  structure
                    ?.event
                  ?? "Yok"
                }
              />

              <DataCard
                title="Swing High"
                value={
                  formatNumber(
                    structure
                      ?.last_swing_high,
                    2,
                  )
                }
              />

              <DataCard
                title="Swing Low"
                value={
                  formatNumber(
                    structure
                      ?.last_swing_low,
                    2,
                  )
                }
              />

              <DataCard
                title="Recent Structure"
                value={
                  structure
                    ?.recent_labels
                    ?.join(
                      " → ",
                    )
                  ?? "—"
                }
              />

              <DataCard
                title="Regime"
                value={
                  regime
                    ?.regime
                  ?? "—"
                }
              />
            </div>
          </Section>


          {/* VOLUME + ORDERFLOW */}

          <Section
            title="Volume & Order Flow"
          >
            <div
              className="
                grid
                grid-cols-2
                gap-3
                lg:grid-cols-3
              "
            >
              <DataCard
                title="Volume"
                value={
                  formatNumber(
                    volume?.volume,
                    3,
                  )
                }
              />

              <DataCard
                title="RVOL"
                value={
                  formatNumber(
                    volume?.rvol,
                    3,
                  )
                }
              />

              <DataCard
                title="Volume Acceleration"
                value={
                  formatNumber(
                    volume
                      ?.volume_acceleration,
                    3,
                  )
                }
              />

              <DataCard
                title="Buy Volume"
                value={
                  formatNumber(
                    orderFlow
                      ?.buy_volume,
                    3,
                  )
                }
              />

              <DataCard
                title="Sell Volume"
                value={
                  formatNumber(
                    orderFlow
                      ?.sell_volume,
                    3,
                  )
                }
              />

              <DataCard
                title="Delta"
                value={
                  formatNumber(
                    orderFlow
                      ?.delta,
                    3,
                  )
                }
              />

              <DataCard
                title="CVD"
                value={
                  formatNumber(
                    orderFlow
                      ?.cvd,
                    3,
                  )
                }
              />

              <DataCard
                title="Buy Ratio"
                value={
                  formatNumber(
                    orderFlow
                      ?.buy_ratio,
                    3,
                  )
                }
              />

              <DataCard
                title="Sell Ratio"
                value={
                  formatNumber(
                    orderFlow
                      ?.sell_ratio,
                    3,
                  )
                }
              />
            </div>
          </Section>


          {/* ORDERBOOK */}

          <Section
            title="Order Book"
          >
            <div
              className="
                grid
                grid-cols-2
                gap-3
                lg:grid-cols-3
              "
            >
              <DataCard
                title="Spread"
                value={
                  formatNumber(
                    orderBook
                      ?.spread,
                    5,
                  )
                }
              />

              <DataCard
                title="Spread BPS"
                value={
                  formatNumber(
                    orderBook
                      ?.spread_bps,
                    5,
                  )
                }
              />

              <DataCard
                title="Imbalance"
                value={
                  formatNumber(
                    orderBook
                      ?.imbalance,
                    4,
                  )
                }
              />

              <DataCard
                title="Pressure"
                value={
                  orderBook
                    ?.pressure
                  ?? "—"
                }
              />

              <DataCard
                title="Microprice"
                value={
                  formatNumber(
                    orderBook
                      ?.microprice,
                    2,
                  )
                }
              />

              <DataCard
                title="Book Sync"
                value={
                  orderBook
                    ?.synced
                    ? "SYNCED"
                    : "NOT SYNCED"
                }
                valueClassName={
                  orderBook
                    ?.synced
                    ? "text-emerald-400"
                    : "text-red-400"
                }
              />
            </div>
          </Section>


          {/* DERIVATIVES */}

          <Section
            title="Derivatives"
          >
            <div
              className="
                grid
                grid-cols-2
                gap-3
                lg:grid-cols-3
              "
            >
              <DataCard
                title="Open Interest"
                value={
                  formatNumber(
                    derivatives
                      ?.open_interest,
                    3,
                  )
                }
              />

              <DataCard
                title="OI Change"
                value={
                  formatPercent(
                    derivatives
                      ?.oi_change_pct,
                    3,
                  )
                }
              />

              <DataCard
                title="Funding Rate"
                value={
                  derivatives
                    ?.funding_rate
                    !== null
                    &&
                    derivatives
                      ?.funding_rate
                    !== undefined

                    ? `${(
                        derivatives
                          .funding_rate
                        * 100
                      ).toFixed(
                        5,
                      )}%`

                    : "—"
                }
              />

              <DataCard
                title="Funding Bias"
                value={
                  derivatives
                    ?.funding_bias
                  ?? "—"
                }
              />

              <DataCard
                title="Price Change"
                value={
                  formatPercent(
                    derivatives
                      ?.price_change_pct,
                    3,
                  )
                }
              />

              <DataCard
                title="Price / OI"
                value={
                  derivatives
                    ?.price_oi_relation
                  ?? "—"
                }
              />
            </div>
          </Section>


          {/* VOLATILITY */}

          <Section
            title="Volatility"
          >
            <div
              className="
                grid
                grid-cols-2
                gap-3
              "
            >
              <DataCard
                title="ATR"
                value={
                  formatNumber(
                    volatility?.atr,
                    3,
                  )
                }
              />

              <DataCard
                title="ATR %"
                value={
                  formatPercent(
                    volatility
                      ?.atr_pct,
                    4,
                  )
                }
              />

              <DataCard
                title="Realized Volatility"
                value={
                  formatNumber(
                    volatility
                      ?.realized_volatility,
                    4,
                  )
                }
              />

              <DataCard
                title="State"
                value={
                  volatility
                    ?.state
                  ?? "—"
                }
              />
            </div>
          </Section>

        </div>


        {/* LEVELS */}

        <div
          className="
            mt-5
          "
        >
          <Section
            title="Support / Resistance"
          >
            <div
              className="
                grid
                gap-5
                lg:grid-cols-2
              "
            >
              <div>
                <div
                  className="
                    mb-3
                    text-sm
                    font-semibold
                    text-emerald-400
                  "
                >
                  SUPPORT
                </div>

                <div
                  className="
                    space-y-2
                  "
                >
                  {levels
                    ?.supports
                    ?.map(
                      (
                        level,
                        index,
                      ) => (
                        <div
                          key={
                            `${level.price}-${index}`
                          }
                          className="
                            flex
                            justify-between
                            rounded-lg
                            border
                            border-neutral-900
                            bg-neutral-950
                            p-3
                          "
                        >
                          <span>
                            $
                            {formatNumber(
                              level.price,
                              2,
                            )}
                          </span>

                          <span
                            className="
                              text-neutral-500
                            "
                          >
                            Strength:
                            {" "}
                            {level.strength}
                            {" · "}
                            {formatPercent(
                              level.distance_pct,
                              3,
                            )}
                          </span>
                        </div>
                      ),
                    )}
                </div>
              </div>


              <div>
                <div
                  className="
                    mb-3
                    text-sm
                    font-semibold
                    text-red-400
                  "
                >
                  RESISTANCE
                </div>

                <div
                  className="
                    space-y-2
                  "
                >
                  {levels
                    ?.resistances
                    ?.map(
                      (
                        level,
                        index,
                      ) => (
                        <div
                          key={
                            `${level.price}-${index}`
                          }
                          className="
                            flex
                            justify-between
                            rounded-lg
                            border
                            border-neutral-900
                            bg-neutral-950
                            p-3
                          "
                        >
                          <span>
                            $
                            {formatNumber(
                              level.price,
                              2,
                            )}
                          </span>

                          <span
                            className="
                              text-neutral-500
                            "
                          >
                            Strength:
                            {" "}
                            {level.strength}
                            {" · "}
                            {formatPercent(
                              level.distance_pct,
                              3,
                            )}
                          </span>
                        </div>
                      ),
                    )}
                </div>
              </div>
            </div>
          </Section>
        </div>


        {/* DATA QUALITY */}

        <div
          className="
            mt-5
          "
        >
          <Section
            title="Data Quality"
          >
            <div
              className="
                grid
                grid-cols-2
                gap-3
                lg:grid-cols-4
              "
            >
              <DataCard
                title="Stale"
                value={
                  health?.stale
                    ? "YES"
                    : "NO"
                }
                valueClassName={
                  health?.stale
                    ? "text-red-400"
                    : "text-emerald-400"
                }
              />

              <DataCard
                title="Missing Candles"
                value={
                  String(
                    health
                      ?.missing_candles
                    ?? 0,
                  )
                }
              />

              <DataCard
                title="Orderbook"
                value={
                  health
                    ?.orderbook_synced
                    ? "SYNCED"
                    : "NOT SYNCED"
                }
              />

              <DataCard
                title="Errors"
                value={
                  String(
                    health
                      ?.errors
                      ?.length
                    ?? 0,
                  )
                }
              />
            </div>
          </Section>
        </div>


        <footer
          className="
            py-10
            text-center
            text-xs
            text-neutral-700
          "
        >
          Binance Futures AI Market Intelligence
          · deterministic analytics
        </footer>

      </div>
    </main>
  )
}