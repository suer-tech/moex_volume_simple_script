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