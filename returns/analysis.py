import datetime
import multiprocessing
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from returns.models import *

def aggregate_returns(returns_data, show=False):
    # returns_data = [(date, return frac, time span, model_name), ...]
    r_data = np.array(returns_data).T
    ts = r_data[2].astype(float)[0]
    mn = r_data[3][0]
    rf = r_data[1].astype(float)
    r_losers = np.count_nonzero(rf < 0.0) / len(rf)
    r_mean = np.mean(rf)
    r_median = np.median(rf)
    r_std = np.std(rf)
    r_hist = np.histogram(rf, bins=45)
    r_mode = r_hist[1][np.argmax(r_hist[0])]
    if show:
        print(f"### AGGREGATE RETURNS ### {mn} ###")
        print(f"Time span = {ts:5.2f} years")
        print(f"Mean = {r_mean:5.2%}")
        print(f"Median = {r_median:5.2%}")
        print(f"Mode = {r_mode:5.2%}")
        print(f"StDev = {r_std:5.2%}")
        print(f"Losing start days = {r_losers:5.2%}")
        _ = plt.hist(rf, bins=45)
        plt.title("Sample Returns")
        plt.show()
    return ts, r_losers, r_mean, r_median, r_mode, r_std, mn

def plot_trend(trend, index=1):
    _trend = np.array(trend).T[:index+1]
    plt.plot(_trend[0].astype(float), _trend[index].astype(float))
    plt.ylabel("% lossy start days")
    plt.xlabel("years returns")


