import asyncio
from api import get_shares_list, get_candles
import numpy as np


async def calculate_average_vol(quote_arr):
    volumes = [candle.volume for data in quote_arr for candle in data]
    return np.mean(volumes)


async def main():
    shares = get_shares_list()
    shares_name_dict = {a.figi: a.name for a in shares}

    tasks = []
    for figi, name in shares_name_dict.items():
        candles_info = asyncio.create_task(get_candles(figi, name))
        tasks.append(candles_info)
    all_candle_data = await asyncio.gather(*tasks)

    for quote in all_candle_data:
        data = list(quote.values())
        if data and data[0]:
            avrg_vol = await calculate_average_vol(data)
            last_volume = data[0][-1].volume
            # print(quote.keys())
            # print(f'avrg_vol = {avrg_vol}')
            # print(f'last_volume = {last_volume}')
            # print('')
            if last_volume > avrg_vol * 3:
                print(quote.keys())
            print('')

# Запуск асинхронного кода
asyncio.run(main())
