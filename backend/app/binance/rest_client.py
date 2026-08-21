from __future__ import annotations

import httpx

from app.binance.schemas import (
    Candle,
    FundingRate,
    OpenInterest,
)
from app.config import settings


class BinanceRESTError(Exception):
    pass


class BinanceFuturesRESTClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = (
            base_url
            or settings.binance_rest_base_url
        ).rstrip("/")

        self.timeout = timeout

    async def _get(
        self,
        path: str,
        params: dict | None = None,
    ):
        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
            ) as client:
                response = await client.get(
                    url,
                    params=params,
                )

                response.raise_for_status()

                return response.json()

        except httpx.HTTPStatusError as exc:
            raise BinanceRESTError(
                f"Binance HTTP error: "
                f"{exc.response.status_code} "
                f"{exc.response.text}"
            ) from exc

        except httpx.RequestError as exc:
            raise BinanceRESTError(
                f"Binance connection error: {exc}"
            ) from exc

    async def get_klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "5m",
        limit: int = 300,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[Candle]:

        params: dict[str, str | int] = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit,
        }

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        raw_klines = await self._get(
            "/fapi/v1/klines",
            params=params,
        )

        candles: list[Candle] = []

        for row in raw_klines:
            candles.append(
                Candle(
                    open_time=int(row[0]),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=float(row[5]),
                    close_time=int(row[6]),
                    quote_volume=float(row[7]),
                    trades=int(row[8]),
                    taker_buy_base_volume=float(row[9]),
                    taker_buy_quote_volume=float(
                        row[10]
                    ),
                    symbol=symbol.upper(),
                    interval=interval,
                    closed=True,
                )
            )

        return candles

    async def get_open_interest(
        self,
        symbol: str = "BTCUSDT",
    ) -> OpenInterest:

        raw = await self._get(
            "/fapi/v1/openInterest",
            params={
                "symbol": symbol.upper(),
            },
        )

        return OpenInterest(
            symbol=raw["symbol"],
            open_interest=float(
                raw["openInterest"]
            ),
            time=int(raw["time"])
            if raw.get("time") is not None
            else None,
        )

    async def get_funding_history(
        self,
        symbol: str = "BTCUSDT",
        limit: int = 100,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[FundingRate]:

        params: dict[str, str | int] = {
            "symbol": symbol.upper(),
            "limit": limit,
        }

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        raw_items = await self._get(
            "/fapi/v1/fundingRate",
            params=params,
        )

        results: list[FundingRate] = []

        for item in raw_items:
            mark_price = item.get("markPrice")

            results.append(
                FundingRate(
                    symbol=item["symbol"],
                    funding_rate=float(
                        item["fundingRate"]
                    ),
                    funding_time=int(
                        item["fundingTime"]
                    ),
                    mark_price=(
                        float(mark_price)
                        if mark_price is not None
                        else None
                    ),
                )
            )

        return results

    async def get_order_book_snapshot(
        self,
        symbol: str = "BTCUSDT",
        limit: int = 1000,
    ) -> dict:

        raw = await self._get(
            "/fapi/v1/depth",
            params={
                "symbol": symbol.upper(),
                "limit": limit,
            },
        )

        return {
            "lastUpdateId": int(
                raw["lastUpdateId"]
            ),
            "E": int(
                raw.get("E", 0)
            ),
            "T": int(
                raw.get("T", 0)
            ),
            "bids": [
                [
                    float(level[0]),
                    float(level[1]),
                ]
                for level in raw.get(
                    "bids",
                    [],
                )
            ],
            "asks": [
                [
                    float(level[0]),
                    float(level[1]),
                ]
                for level in raw.get(
                    "asks",
                    [],
                )
            ],
        }


binance_rest_client = (
    BinanceFuturesRESTClient()
)