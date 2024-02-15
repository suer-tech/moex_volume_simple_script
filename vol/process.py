import glob
import asyncio

import emoji

from api import get_shares_list, get_candles, get_ticker
from calculate import calculate_proc, calculate_average_vol


async def get_all_candle_data():
    shares = await get_shares_list()
    shares_name_dict = {a.figi: a.name for a in shares}

    tasks = []
    semaphore = asyncio.Semaphore(250)
    for figi, name in shares_name_dict.items():
        async with semaphore:
            candles_info = asyncio.create_task(get_candles(figi, name))
            tasks.append(candles_info)
    result = await asyncio.gather(*tasks)
    print(type(result))
    return result


async def write_data(key, value):
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

        res_proc = "🟢" if float(proc) > 0 else "🔴"
        if 4 > float(x) > 3:
            res_x = '‼️'
        elif float(x) > 4:
            res_x = '🧨🧨🧨'
        else:
            res_x = '❗️'

        result = (
                  f"{res_proc}{ticker}: {proc}%\n"
                  f"{res_x}{key}: x {x}\n"
                  f"💰Объём сессии: {last_volume}\n"
                  f"📊Средний обьём за неделю: {int(avrg_vol)}\n\n"
                  )

        with open(f"{ticker}.txt", "w", encoding='utf-8') as file:
            file.write(result)


async def delete_txt():
    files = glob.glob('/*.txt')

    if files:
        for f in files:
            try:
                f.unlink()
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))


async def main():
    while True:
        all_candle_data = await get_all_candle_data()
        res = [await write_data(key, value) for candle_data in all_candle_data for key, value in candle_data.items() if value]

        await asyncio.sleep(300)
        await delete_txt()


if __name__ == '__main__':
    asyncio.run(main())
