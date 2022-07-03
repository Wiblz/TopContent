N = 14  # two weeks
ALPHA = 2 / (N + 1)  # smoothing factor


def EMA(prev_ema, new_avg):
    return ALPHA * new_avg + (1 - ALPHA) * prev_ema if prev_ema != 0 else new_avg
