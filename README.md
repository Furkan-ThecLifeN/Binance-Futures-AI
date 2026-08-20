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

değerlendirmelerinden birini oluşturmaktır.
Sayısal hesaplamalar mümkün olduğunca AI'ye bırakılmaz.
EMA, RSI, ATR, VWAP, market structure, order flow, order book, volatility ve confluence gibi hesaplamalar backend tarafından deterministik olarak üretilir.
🏗️ Teknoloji Stack'i
Frontend
React
Vite
TypeScript
Tailwind CSS
shadcn/ui
TanStack Query
Zustand
TradingView Lightweight Charts

Frontend'in temel görevleri:
Dashboard
Market Scanner
Coin/Symbol Detail
Canlı grafikler
Sistem health görüntüleme
Snapshot oluşturma
Snapshot indirme
Trading Journal
Backend
Python
FastAPI
Pydantic
asyncio
httpx
websockets
pandas
NumPy
SciPy
TA-Lib / pandas-ta

Backend;
Binance bağlantısını,
WebSocket yönetimini,
REST backfill işlemlerini,
analytics hesaplamalarını,
snapshot üretimini,
API katmanını
yönetir.
Database
PostgreSQL
TimescaleDB
Redis

PostgreSQL / TimescaleDB
Geçmiş ve zaman serisi verileri için kullanılır.
Örnek veriler:
symbols
candles
aggregate_trades
orderbook_metrics
ticker_snapshots
funding_rates
open_interest
long_short_ratios
technical_indicators
market_structure
support_resistance
analysis_snapshots
trade_journal

Redis
Canlı market state için kullanılır.
Örnek:
market:{symbol}:price
market:{symbol}:book
market:{symbol}:oi
market:{symbol}:funding
market:{symbol}:metrics
market:{symbol}:health

📡 Binance Veri Kaynakları
Sistem ağırlıklı olarak Binance USDⓈ-M Futures public market verilerini kullanır.
WebSocket
Gerçek zamanlı veriler:
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

Market Structure
Sistem aşağıdaki yapıları tespit etmeyi hedefler:
HH
HL
LH
LL

Swing High
Swing Low

BOS
CHoCH

Trend
Range
Breakout
Retest

Ayrıca:
Support / Resistance
Previous Day High / Low
Previous Week High / Low
Session High / Low
seviyeleri hesaplanır.
📈 Volume & Order Flow
aggTrade verileri üzerinden:
Buy Initiated Volume
Sell Initiated Volume
Delta
CVD
Trade Velocity
Trade Frequency
Large Trades
Buy/Sell Pressure

gibi metrikler hesaplanır.
📚 Order Book
Order book analizinde:
Spread
Bid Depth
Ask Depth
Imbalance
Liquidity Walls
Depth Pressure
Microprice
Book Pressure

metrikleri kullanılır.
Order book sequence gap oluşursa mevcut local order book güvenilir kabul edilmez ve yeniden oluşturulur.
📉 Derivatives Analizi
Futures piyasasına özgü olarak:
Open Interest
OI Change
Funding Rate
Long/Short Ratio
Top Trader Ratios
Taker Buy/Sell

verileri değerlendirilir.
Price ve Open Interest ilişkisi de piyasa bağlamının bir parçasıdır.
Örneğin sistem:
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

Analizden sonra gerçekleşen fiyat hareketleri de kaydedilebilir:
+5m
+15m
+30m
+1h

Böylece sistemin geçmiş performansı ölçülebilir.
🤖 AI Snapshot
Dashboard üzerindeki:
Generate AI Snapshot

işlemi seçilen coin için analiz paketi oluşturur.
Örnek:
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

analysis.json temel olarak şu bölümleri içerir:
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

🩺 Data Quality
Sistemin önemli tasarım prensiplerinden biri veri kalitesidir.
Kontrol edilen bazı alanlar:
websocket_connected
last_event_age_ms
missing_candles
orderbook_synced
rest_backfill_complete
open_interest_age_seconds
funding_age_seconds
data_integrity_score
snapshot_status

Snapshot durumu:
HEALTHY
DEGRADED
INVALID

Veri eski veya eksikse ya da order book senkronizasyonu bozuksa veri normal ve güvenilir bir snapshot gibi AI'ye gönderilmemelidir.
📁 Proje Yapısı
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

🔌 Backend API
Planlanan temel API:
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
03 → Docker + PostgreSQL/TimescaleDB + Redis
04 → Binance Data Layer
05 → Normalize + Validate + Store
06 → Analytics Engine V1
07 → Confluence Score
08 → API + Live Symbol Screen
09 → Market Scanner
10 → AI Snapshot
11 → ChatGPT Analysis + Journal
12 → Tests + V1 Freeze

Her aşama çalışıp test edilmeden sonraki aşamaya geçilmemesi hedeflenir.
✅ V1 Tamamlanma Kriterleri
V1 aşağıdakiler çalıştığında tamamlanmış kabul edilir:
React dashboard çalışıyor.
Backend health bilgisi frontend'de görüntüleniyor.
BTCUSDT/SOLUSDT gibi sembollerin canlı fiyatı alınabiliyor.
5 dakikalık mumlar UI'da canlı güncelleniyor.
WebSocket kopması sonrası otomatik reconnect çalışıyor.
Historical candle verileri saklanıyor.
EMA / RSI / ATR / VWAP hesaplanıyor.
Market structure hesaplanıyor.
RVOL hesaplanıyor.
OI ve Funding verileri alınıyor.
Temel order flow hesaplanıyor.
Temel order book analizi yapılıyor.
LONG / SHORT Confluence Score oluşturuluyor.
Scanner likit USDT perpetual coinleri sıralayabiliyor.
AI Snapshot oluşturulabiliyor.
analysis.json üretilebiliyor.
Candle CSV dosyaları üretilebiliyor.
Data quality snapshot içinde bulunuyor.
Snapshot ChatGPT tarafından analiz edilebiliyor.
Sonuçlar Journal'a kaydedilebiliyor.
Analizler sonraki fiyat hareketleriyle karşılaştırılabiliyor.
⚠️ Risk Uyarısı
Bu proje finansal tavsiye veya garantili işlem sinyali üretmek amacıyla tasarlanmamıştır.
Futures işlemleri yüksek risk içerir.
Sistemin ürettiği:
LONG
SHORT
NO TRADE
Confluence Score
Market Regime

gibi çıktılar araştırma ve karar desteği amacıyla kullanılmalıdır.
Özellikle Confluence Score bir kazanma olasılığı veya garanti edilmiş başarı oranı değildir.
Current Status
🚧 Development / V1
Şu anki temel hedef:
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
