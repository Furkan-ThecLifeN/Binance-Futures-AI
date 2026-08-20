Binance Futures AI Market Intelligence
Binance USDⓈ-M Futures piyasalarından gerçek zamanlı ve geçmiş verileri toplayan, teknik analiz ve piyasa mikro-yapı metriklerini deterministik olarak hesaplayan ve sonuçları AI destekli analiz için paketleyen full-stack market intelligence sistemi.
Amaç: Otomatik işlem açan bir trading bot geliştirmek değil; özellikle kısa vadeli ve 5 dakikalık futures analizlerinde kullanılabilecek ölçülebilir, veri odaklı bir karar destek altyapısı oluşturmaktır.
🎯 Projenin Amacı
Binance Futures AI Market Intelligence, Binance Futures piyasasından gelen verileri tek bir analiz altyapısında birleştirir.
Sistem:
Binance USDⓈ-M Futures'tan canlı ve geçmiş piyasa verilerini toplar.
Gelen verileri normalize eder ve veri kalitesini kontrol eder.
Teknik indikatörleri hesaplar.
Market structure analizi yapar.
Volume ve order flow metriklerini üretir.
Order book yapısını analiz eder.
Open Interest, Funding Rate ve diğer derivatives verilerini değerlendirir.
Multi-timeframe piyasa bağlamı oluşturur.
LONG ve SHORT tarafı için deterministik Confluence Score hesaplar.
Kullanıcının seçtiği coin için bir AI Snapshot oluşturur.
Snapshot verilerini JSON, CSV ve gerektiğinde grafik olarak dışa aktarır.
Bu paket ChatGPT'ye yüklenerek senaryo ve risk analizi yapılabilir.
Temel akış:
Binance Futures
       ↓
Python Market Collector
       ↓
Normalize + Validate
       ↓
PostgreSQL / TimescaleDB
       +
      Redis
       ↓
Analytics Engine
       ↓
Confluence Engine
       ↓
React Dashboard
       ↓
AI Snapshot
       ↓
JSON + CSV + Charts
       ↓
ChatGPT
       ↓
LONG / SHORT / NO TRADE
       ↓
Journal + Performance Measurement

🧠 AI'nin Rolü
Bu projede AI doğrudan trade açan veya emir veren bir sistem değildir.
AI'nin görevi:
piyasa senaryolarını karşılaştırmak,
bullish ve bearish argümanları değerlendirmek,
confluence analizi yapmak,
riskleri belirtmek,
invalidation noktalarını değerlendirmek,
karşı görüş üretmek,
sonuç olarak:
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
mark price

Ana timeframe:
5m

Desteklenen analiz timeframe'leri:
TimeframeKullanım1mExecution / micro move3mKısa mikro-yapı5mAna setup15mConfirmation1hIntraday trend4hHigher timeframe contextREST API
REST API ağırlıklı olarak:
historical candles,
backfill,
Open Interest,
funding rate,
funding history,
long/short ratios,
top trader ratios,
taker buy/sell verileri,
24h ticker,
symbol metadata
için kullanılır.
Gerçek zamanlı veriler mümkün olduğunca WebSocket üzerinden alınır.
📊 Analytics Engine
Analytics Engine projenin ana hesaplama katmanıdır.
Teknik İndikatörler
İlk sürümde:
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

kombinasyonlarını sınıflandırabilir.
🔥 Confluence Score
AI'den bağımsız olarak backend tarafından LONG ve SHORT için 0–100 setup score oluşturulur.
Başlangıç ağırlıkları:
FaktörMaksimum PuanTrend Alignment15Market Structure15Momentum10Volume10Order Flow10Order Book10Derivatives10Support / Resistance10Volatility Suitability5Risk / Reward Context5Toplam100
Çıktı:
{
  "long_score": 0,
  "short_score": 0
}

Bu değerler gerçek kazanma olasılığı değildir.
Score yalnızca mevcut piyasa verilerinin ilgili setup ile ne kadar uyumlu olduğunu ifade eder.
🔍 Market Scanner
Scanner tüm USDT perpetual piyasasını takip eder.
Akış:
All USDT Perpetual Symbols
          ↓
      Light Scanner
          ↓
   Top 10–20 Candidates
          ↓
      Deep Streams
          ↓
Full Analytics + Order Flow
          ↓
Top Long / Top Short / Avoid

Scanner ekranında örneğin:
Symbol
Price
Volume
RVOL
5m Trend
15m Trend
1h Trend
OI Change
Funding
Volatility
Long Score
Short Score

gösterilebilir.
🖥️ Frontend Ekranları
Dashboard
Genel sistem durumunu gösterir.
Örneğin:
Backend Status
WebSocket Status
aktif symbol sayısı
data quality
Top Long adayları
Top Short adayları
snapshot kısayolları
Scanner
USDT perpetual piyasasını tarayan ana ekran.
Coin'ler hesaplanan market metriklerine göre karşılaştırılabilir.
Symbol Detail
Tek bir coin için ayrıntılı analiz ekranıdır.
Örneğin:
Candlestick Chart
Timeframe Selector
Price
Trend
RSI
ATR
VWAP
Volume
Market Structure
Order Flow
Order Book
Open Interest
Funding
Support / Resistance
Long Score
Short Score

Snapshots
Üretilmiş AI Snapshot paketlerinin yönetildiği ekran.
Snapshot:
oluşturulabilir,
listelenebilir,
indirilebilir,
yeniden üretilebilir.
Journal
Analizlerin sonuçlarının ölçülmesini sağlar.
Örneğin:
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
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ScannerPage.tsx
│   │   │   ├── SymbolPage.tsx
│   │   │   ├── SnapshotsPage.tsx
│   │   │   └── JournalPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── socket.ts
│   │   ├── stores/
│   │   │   └── marketStore.ts
│   │   ├── types/
│   │   │   └── market.ts
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   ├── binance/
│   │   ├── market_data/
│   │   ├── analytics/
│   │   ├── scanner/
│   │   ├── snapshots/
│   │   ├── database/
│   │   ├── cache/
│   │   └── tests/
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/
│   ├── snapshots/
│   └── exports/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md

🔌 Backend API
Planlanan temel API:
GET  /api/health

GET  /api/symbols

GET  /api/market/{symbol}
GET  /api/market/{symbol}/candles?interval=5m
GET  /api/market/{symbol}/orderbook
GET  /api/market/{symbol}/derivatives

GET  /api/analytics/{symbol}

GET  /api/scanner
GET  /api/scanner/long
GET  /api/scanner/short

POST /api/snapshots/{symbol}/generate
GET  /api/snapshots
GET  /api/snapshots/{id}/download

GET  /api/journal
POST /api/journal

WS   /ws/market/{symbol}

🔐 Güvenlik
V1 yalnızca market intelligence ve karar desteği sistemidir.
İlk sürümde:
❌ Otomatik emir açma
❌ Withdrawal
❌ Binance secret'ın frontend'e verilmesi
❌ AI tarafından doğrudan trade execution

✅ Public market data
✅ Read-only architecture
✅ Deterministic analytics
✅ Data quality validation

Public endpoint'ler yeterliyse Binance API key kullanılması gerekmez.
İleride hesap veya pozisyon verileri eklenecekse ayrı bir read-only API key, IP whitelist ve backend .env secret yönetimi kullanılmalıdır.
🚀 Geliştirme Yol Haritası
Proje aşağıdaki sırayla geliştirilecektir:
01 → Monorepo + React/Vite/TypeScript
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

İlk milestone, çalışan React/Vite/TypeScript frontend + Backend Status dashboard temelini oluşturmaktır.
