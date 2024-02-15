import asyncio
from datetime import timedelta

from tinkoff.invest import AsyncClient, CandleInterval
from tinkoff.invest.utils import now

from config import tinkoff

TOKEN = tinkoff


async def get_shares_list():
    all_shares = []
    async with AsyncClient(TOKEN) as client:
        r = await client.instruments.shares(instrument_status=2)
        for i in r.instruments:
            if i.class_code == 'TQBR':
                all_shares.append(i)
        print(len(all_shares))
        return all_shares


async def get_candles(figi, name):
    all_candles = []
    interval = CandleInterval.CANDLE_INTERVAL_DAY
    _from = now() - timedelta(days=10)
    async with AsyncClient(TOKEN) as client:
        try:
            async for candle in client.get_all_candles(
                    figi=figi,
                    from_=_from,
                    interval=interval,
            ):
                all_candles.append(candle)
        except Exception as e:
            print(f"Произошла ошибка при получении свечей: {e}")
        return {name: all_candles}


async def get_ticker(ticker: str):
    async with AsyncClient(TOKEN) as client:
        data = await client.instruments.find_instrument(query=ticker, instrument_kind=2)
        return data.instruments[0].ticker
