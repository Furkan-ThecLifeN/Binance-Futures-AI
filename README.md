# Binance Futures AI Market Intelligence

> Real-time Binance USDⓈ-M Futures market intelligence, deterministic quantitative analytics, market scanning, and AI-assisted scenario analysis.

**Binance Futures AI Market Intelligence** is a full-stack market analysis platform designed to collect real-time and historical Binance Futures data, calculate technical and market microstructure metrics, rank trading setups, and generate structured analysis packages for AI-assisted evaluation.

The system is designed primarily around **short-term and 5-minute futures market analysis**.

> [!IMPORTANT]
> This project is **not an automated trading bot**.
> V1 does not place orders, execute trades, or require withdrawal permissions. It is designed as a read-only market intelligence and decision-support system.

---

## 🎯 Project Goals

The platform combines multiple layers of futures market data into a single analysis pipeline.

It is designed to:

* Collect real-time Binance Futures market data
* Retrieve and store historical market data
* Validate and normalize incoming data
* Calculate technical indicators
* Detect market structure
* Analyze volume and order flow
* Analyze order book liquidity
* Track Open Interest and Funding Rate
* Build multi-timeframe market context
* Calculate deterministic LONG and SHORT Confluence Scores
* Scan USDT perpetual markets for interesting setups
* Generate structured AI Snapshots
* Export analysis as JSON, CSV, and optional charts
* Evaluate analysis results against future price movement

---

## 🏗️ System Architecture

```text
Binance USDⓈ-M Futures
          │
          ├── WebSocket
          │   ├── Klines
          │   ├── AggTrades
          │   ├── Book Ticker
          │   └── Depth
          │
          └── REST API
              ├── Historical Candles
              ├── Open Interest
              ├── Funding
              └── Market Metadata
                    │
                    ▼
           Python Market Collector
                    │
                    ▼
           Normalize + Validate
                    │
             ┌──────┴──────┐
             ▼             ▼
      PostgreSQL /      Redis
      TimescaleDB      Live State
             └──────┬──────┘
                    ▼
            Analytics Engine
                    │
                    ▼
           Confluence Engine
                    │
             ┌──────┴──────┐
             ▼             ▼
      React Dashboard   AI Snapshot
                            │
                            ▼
                    JSON + CSV + Charts
                            │
                            ▼
                         ChatGPT
                            │
                            ▼
                LONG / SHORT / NO TRADE
                            │
                            ▼
                 Journal + Measurement
```

---

## 🧠 AI Role

AI is used as the **final reasoning and scenario-analysis layer**, not as the numerical calculation engine.

The AI can evaluate:

* Bullish and bearish scenarios
* Market context
* Confluence
* Risk factors
* Invalidation conditions
* Conflicting signals
* Alternative interpretations

Possible analysis outcomes include:

```text
LONG BIAS
SHORT BIAS
NO TRADE
```

Technical calculations are performed deterministically by the backend.

Metrics such as:

* EMA
* RSI
* ATR
* VWAP
* Market Structure
* Volume
* Order Flow
* Order Book
* Open Interest
* Funding
* Volatility
* Confluence Score

are calculated before the data reaches the AI layer.

---

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* TypeScript
* Tailwind CSS
* shadcn/ui
* TanStack Query
* Zustand
* TradingView Lightweight Charts

### Backend

* Python
* FastAPI
* Pydantic
* asyncio
* httpx
* websockets
* pandas
* NumPy
* SciPy
* TA-Lib / pandas-ta

### Data & Infrastructure

* PostgreSQL
* TimescaleDB
* Redis
* Docker
* Docker Compose

### Testing

* pytest
* Vitest
* Playwright

---

## 📡 Binance Market Data

The system primarily uses Binance USDⓈ-M Futures public market data.

### WebSocket Streams

Real-time streams include:

```text
kline
aggTrade
bookTicker
depth
markPrice
```

WebSocket is preferred for continuously changing market data.

REST is primarily used for initialization, historical data, slower-moving metrics, and recovery.

### REST Data

REST endpoints are used for:

* Historical candles
* Open Interest
* Open Interest history
* Funding Rate
* Funding history
* Long/Short ratios
* Top Trader ratios
* Taker buy/sell statistics
* 24h ticker data
* Exchange metadata
* Symbol metadata
* Missing candle backfill

---

## ⏱️ Multi-Timeframe Analysis

The main setup timeframe is **5 minutes**.

| Timeframe | Purpose                    |
| --------- | -------------------------- |
| `1m`      | Execution / micro movement |
| `3m`      | Short-term microstructure  |
| `5m`      | Primary setup              |
| `15m`     | Confirmation               |
| `1h`      | Intraday trend             |
| `4h`      | Higher-timeframe context   |

The system combines these timeframes instead of evaluating the 5-minute chart in isolation.

---

## 📊 Analytics Engine

The analytics engine is responsible for deterministic market calculations.

### Technical Indicators

Initial V1 indicators include:

```text
EMA 9 / 20 / 50 / 100 / 200
SMA 20 / 50 / 200
RSI 7 / 14
MACD
ATR 14
ATR %
ADX 14
VWAP
Bollinger Bands
Stochastic RSI
```

---

## 🧭 Market Structure

The structure engine detects concepts such as:

```text
HH / HL / LH / LL

Swing High
Swing Low

BOS
CHoCH

Trend
Range
Breakout
Retest
```

It also calculates important price levels including:

* Support / Resistance
* Previous Day High / Low
* Previous Week High / Low
* Session High / Low
* Distance to key levels
* Level strength

---

## 📈 Volume & Order Flow

Aggregate trade data is used to calculate:

* Buy-initiated volume
* Sell-initiated volume
* Delta
* CVD
* Buy/Sell pressure
* Trade velocity
* Trade frequency
* Large trade activity
* Relative volume

This provides additional context beyond traditional candle-based indicators.

---

## 📚 Order Book Analytics

Order book analysis includes:

* Spread
* Spread in basis points
* Bid depth
* Ask depth
* Order book imbalance
* Liquidity walls
* Depth pressure
* Microprice
* Book pressure

Order book synchronization is treated as a critical data-quality requirement.

If a sequence gap is detected, the local order book must be considered invalid and rebuilt.

---

## 📉 Futures & Derivatives Analytics

The system evaluates futures-specific metrics including:

* Open Interest
* OI change
* Funding Rate
* Long/Short Ratio
* Top Trader ratios
* Taker Buy/Sell statistics

Price and Open Interest relationships can also be classified:

```text
Price ↑ + OI ↑
Price ↑ + OI ↓
Price ↓ + OI ↑
Price ↓ + OI ↓
```

These combinations provide additional context for position buildup, closing activity, and market participation.

---

## 🔥 Confluence Score

LONG and SHORT setup scores are calculated by the backend independently from AI.

Each side receives a deterministic score between:

```text
0 ───────────────────────────── 100
```

Initial weighting:

| Factor                 | Max Score |
| ---------------------- | --------: |
| Trend Alignment        |        15 |
| Market Structure       |        15 |
| Momentum               |        10 |
| Volume                 |        10 |
| Order Flow             |        10 |
| Order Book             |        10 |
| Derivatives            |        10 |
| Support / Resistance   |        10 |
| Volatility Suitability |         5 |
| Risk / Reward Context  |         5 |
| **Total**              |   **100** |

Example output:

```json
{
  "long_score": 72,
  "short_score": 34
}
```

> [!NOTE]
> Confluence Score is **not a probability of winning a trade**.
> It represents how strongly current market conditions align with a particular setup.

---

## 🔍 Market Scanner

The scanner is designed to monitor the USDT perpetual futures universe.

```text
All USDT Perpetual Symbols
            │
            ▼
       Light Scanner
            │
            ▼
    Rank Market Candidates
            │
            ▼
     Top 10–20 Symbols
            │
            ▼
       Deep Streams
            │
            ▼
       Full Analytics
            │
            ▼
 Top Long / Top Short / Avoid
```

The scanner can expose metrics such as:

| Metric      | Description              |
| ----------- | ------------------------ |
| Symbol      | Futures symbol           |
| Price       | Current price            |
| Volume      | Market volume            |
| RVOL        | Relative volume          |
| 5m Trend    | Primary setup trend      |
| 15m Trend   | Confirmation trend       |
| 1h Trend    | Intraday context         |
| OI Change   | Open Interest change     |
| Funding     | Current funding rate     |
| Volatility  | Current volatility state |
| Long Score  | LONG confluence          |
| Short Score | SHORT confluence         |

---

## 🖥️ Frontend

The dashboard is divided into several major screens.

### Dashboard

Provides a high-level overview of the system:

* Backend status
* WebSocket status
* Data quality
* Active symbol count
* Top LONG candidates
* Top SHORT candidates
* Snapshot shortcuts

### Scanner

Displays and ranks USDT perpetual markets using lightweight analytics.

### Symbol Detail

Provides detailed analysis for an individual market:

* Candlestick chart
* Timeframe selector
* Current price
* Trend
* RSI
* ATR
* VWAP
* Volume
* Market structure
* Order flow
* Order book
* Open Interest
* Funding
* Support / Resistance
* LONG score
* SHORT score

### Snapshots

Allows generated AI analysis packages to be:

* Created
* Listed
* Downloaded
* Regenerated

### Journal

Stores analysis outcomes for later evaluation.

Possible fields include:

```text
Snapshot ID
Symbol
AI Bias
Long Score
Short Score
Entry
Exit
Fees
MFE
MAE
Result
Notes
```

Performance can later be measured against:

```text
+5m
+15m
+30m
+1h
```

price movement.

---

## 🤖 AI Snapshot

The dashboard provides a:

```text
Generate AI Snapshot
```

action.

A generated package may look like:

```text
data/
└── snapshots/
    └── BTCUSDT/
        └── 2026-08-20_14-35/
            ├── manifest.json
            ├── analysis.json
            ├── candles_1m.csv
            ├── candles_5m.csv
            ├── candles_15m.csv
            ├── candles_1h.csv
            ├── chart_5m.png
            ├── chart_15m.png
            └── chart_1h.png
```

### `analysis.json`

The analysis package contains structured sections such as:

```text
meta
symbol
current_market
timeframes
technical_indicators
market_structure
volume_analysis
order_flow
order_book
derivatives
support_resistance
volatility
market_regime
confluence
raw_data_summary
data_quality
```

The package can then be uploaded to ChatGPT for higher-level scenario analysis.

---

## 🩺 Data Quality

Data quality is a first-class part of the architecture.

The system tracks metrics such as:

```text
websocket_connected
last_event_age_ms
missing_candles
orderbook_synced
rest_backfill_complete
open_interest_age_seconds
funding_age_seconds
data_integrity_score
snapshot_status
```

Snapshot health states:

```text
HEALTHY
DEGRADED
INVALID
```

If market data is stale, incomplete, or the order book is out of sync, the snapshot should not be presented to the AI as normal healthy data.

---

## 📁 Project Structure

```text
futures-ai-market-intelligence/
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   ├── scanner/
│   │   │   ├── market/
│   │   │   └── common/
│   │   │
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ScannerPage.tsx
│   │   │   ├── SymbolPage.tsx
│   │   │   ├── SnapshotsPage.tsx
│   │   │   └── JournalPage.tsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── socket.ts
│   │   │
│   │   ├── stores/
│   │   │   └── marketStore.ts
│   │   │
│   │   ├── types/
│   │   │   └── market.ts
│   │   │
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   ├── binance/
│   │   ├── market_data/
│   │   ├── analytics/
│   │   ├── scanner/
│   │   ├── snapshots/
│   │   ├── database/
│   │   ├── cache/
│   │   └── tests/
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/
│   ├── snapshots/
│   └── exports/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔌 API Design

Planned backend API:

```http
GET  /api/health

GET  /api/symbols

GET  /api/market/{symbol}
GET  /api/market/{symbol}/candles?interval=5m
GET  /api/market/{symbol}/orderbook
GET  /api/market/{symbol}/derivatives

GET  /api/analytics/{symbol}

GET  /api/scanner
GET  /api/scanner/long
GET  /api/scanner/short

POST /api/snapshots/{symbol}/generate
GET  /api/snapshots
GET  /api/snapshots/{id}/download

GET  /api/journal
POST /api/journal

WS   /ws/market/{symbol}
```

---

## 🔐 Security Principles

V1 is intentionally designed around public and read-only market data.

### V1 does not include

* ❌ Automatic trade execution
* ❌ Withdrawal functionality
* ❌ Binance secrets in the frontend
* ❌ AI-controlled order execution

### V1 focuses on

* ✅ Public market data
* ✅ Read-only architecture
* ✅ Deterministic analytics
* ✅ Data validation
* ✅ Data-quality monitoring
* ✅ Measurable analysis results

If account or position information is introduced later, it should use a separate **read-only API key**, IP whitelisting, and backend-only environment variables.

Secrets must never be exposed to the frontend.

---

## 🗺️ Development Roadmap

```text
01 → Monorepo + React / Vite / TypeScript
02 → FastAPI Backend
03 → Docker + PostgreSQL / TimescaleDB + Redis
04 → Binance Data Layer
05 → Normalize + Validate + Store
06 → Analytics Engine V1
07 → Confluence Score
08 → API + Live Symbol Screen
09 → Market Scanner
10 → AI Snapshot
11 → ChatGPT Analysis + Journal
12 → Testing + V1 Freeze
```

Each stage should be functional and tested before moving to the next stage.

---

## ✅ V1 Definition of Done

V1 will be considered complete when:

* [ ] React dashboard is operational
* [ ] Backend health is visible from the frontend
* [ ] Live BTCUSDT/SOLUSDT prices are available
* [ ] 5-minute candles update in real time
* [ ] WebSocket automatically reconnects
* [ ] Missing candles can be backfilled
* [ ] Historical candle data is stored
* [ ] EMA / RSI / ATR / VWAP are calculated
* [ ] Market structure is calculated
* [ ] Relative Volume is calculated
* [ ] Open Interest and Funding are available
* [ ] Basic order flow metrics are calculated
* [ ] Basic order book analytics are available
* [ ] LONG / SHORT Confluence Scores are generated
* [ ] Scanner ranks liquid USDT perpetual markets
* [ ] AI Snapshot can be generated
* [ ] `analysis.json` can be exported
* [ ] Candle CSV files can be exported
* [ ] Data-quality information is included in snapshots
* [ ] Snapshot can be analyzed by ChatGPT
* [ ] Analysis result can be stored in the Journal
* [ ] Analysis can be compared with subsequent price movement

---

## 🚧 Current Status

**Development — V1**

Current milestone:

```text
React + Vite + TypeScript
          ↓
    shadcn/ui Dashboard
          ↓
    FastAPI Health API
          ↓
    Binance Live Data
          ↓
       Analytics
          ↓
        Scanner
          ↓
      AI Snapshot
          ↓
   ChatGPT Analysis
          ↓
        Journal
```

The first milestone is a working **React + Vite + TypeScript frontend with a Backend Status dashboard**.

---

## ⚠️ Disclaimer

This project is intended for **research, market analysis, software development, and decision-support purposes**.

It does not provide financial advice and does not guarantee profitable trading outcomes.

Futures trading involves significant financial risk.

Outputs such as:

```text
LONG
SHORT
NO TRADE
Confluence Score
Market Regime
```

must be interpreted as analytical information rather than guaranteed trading signals.

**Confluence Score is not a win probability.**

---

## 📌 Project Philosophy

```text
Collect → Validate → Calculate → Compare → Analyze → Measure
```

The objective is not to force the system to produce a trade.

**NO TRADE is a valid outcome.**

The system becomes useful only when its analysis can be measured against what actually happens in the market.
