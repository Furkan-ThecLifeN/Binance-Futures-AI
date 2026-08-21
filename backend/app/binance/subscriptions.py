SUPPORTED_KLINE_INTERVALS = (
    "1m",
    "5m",
    "15m",
    "1h",
)


def normalize_symbol(
    symbol: str,
) -> str:
    return symbol.strip().lower()


def build_market_streams(
    symbol: str,
) -> list[str]:
    """
    Binance MARKET WebSocket streams.

    Burada:
    - kline
    - aggTrade

    bulunur.
    """

    symbol = normalize_symbol(
        symbol
    )

    return [
        *[
            f"{symbol}@kline_{interval}"
            for interval
            in SUPPORTED_KLINE_INTERVALS
        ],

        f"{symbol}@aggTrade",
    ]


def build_public_streams(
    symbol: str,
) -> list[str]:
    """
    Binance PUBLIC WebSocket streams.

    Burada:
    - bookTicker
    - depth

    bulunur.
    """

    symbol = normalize_symbol(
        symbol
    )

    return [
        f"{symbol}@bookTicker",
        f"{symbol}@depth@100ms",
    ]


def build_symbol_streams(
    symbol: str,
) -> list[str]:
    """
    Tüm stream isimlerini görmek
    veya debug amacıyla kullanılır.
    """

    return [
        *build_market_streams(
            symbol
        ),

        *build_public_streams(
            symbol
        ),
    ]


def build_btcusdt_streams(
) -> list[str]:
    return build_symbol_streams(
        "BTCUSDT"
    )


def build_combined_stream_url(
    base_url: str,
    streams: list[str],
) -> str:

    base_url = (
        base_url.rstrip("/")
    )

    stream_names = "/".join(
        streams
    )

    return (
        f"{base_url}"
        f"?streams={stream_names}"
    )