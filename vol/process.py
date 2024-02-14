import asyncio

from vol.api import get_shares_list, get_candles, get_ticker
import numpy as np


async def calculate_average_vol(quote_arr):
    volumes = [candle.volume for candle in quote_arr]
    return np.mean(volumes)


async def calculate_proc(price, yest_price):
    p = float(price)
    yp = float(yest_price)
    if p > yp:
        return f'+{round((p - yp) / (yp / 100), 2)}'

    return f'-{round((yp - p) / (yp / 100), 2)}'


async def main():
    shares = await get_shares_list()
    shares_name_dict = {a.figi: a.name for a in shares}

    tasks = []
    semaphore = asyncio.Semaphore(250)
    for figi, name in shares_name_dict.items():
        async with semaphore:
            candles_info = asyncio.create_task(get_candles(figi, name))
            tasks.append(candles_info)
    all_candle_data = await asyncio.gather(*tasks)

    for candle_data in all_candle_data:
        for key, value in candle_data.items():
            if value:
                val_list = list(value)
                avrg_vol = await calculate_average_vol(val_list)
                last = val_list[-1]
                last_volume = last.volume
                if last_volume > avrg_vol * 2:
                    yest_price = f"{val_list[-2].close.units}.{val_list[-2].close.nano}"
                    price = f"{last.close.units}.{last.close.nano}"
                    proc = await calculate_proc(price, yest_price)
                    ticker = await get_ticker(key)
                    x = round(last_volume / avrg_vol, 1)
                    result = f"{ticker}\n{key}: x {x}\nОбъём сессии: {last_volume}\nСредний обьём за неделю: {avrg_vol}\nЦена:{proc}\n\n"

                    with open(f"{ticker}.txt", "w") as file:
                        file.write(result)
