from datetime import timedelta

from tinkoff.invest import AsyncClient, CandleInterval, Client
from tinkoff.invest.utils import now

from config import TOKEN


def get_shares_list():
    all_shares = []
    with Client(TOKEN) as client:
        r = client.instruments.shares(instrument_status=2)
        for i in r.instruments:
            if i.class_code == 'TQBR':
                all_shares.append(i)
        print(len(all_shares))
        return all_shares


async def get_candles(figi, name):
    all_candles = []
    interval = CandleInterval.CANDLE_INTERVAL_HOUR
    _from = now() - timedelta(days=10)
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
                figi=figi,
                from_=_from,
                interval=interval,
        ):
            all_candles.append(candle)

        return {name: all_candles}
