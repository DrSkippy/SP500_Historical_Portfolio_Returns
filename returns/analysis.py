import datetime
import multiprocessing
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from returns.models import *

def aggregate_returns(returns_data, show=False):
    # returns_data = [(date, return frac, time span, model_name), ...]
    r_data = np.array(returns_data).T
    ts = r_data[2].astype(int)[0]
    mn = r_data[3][0]
    rf = r_data[1].astype(float)
    r_losers = np.count_nonzero(rf < 0.0) / len(rf)
    r_mean = np.mean(rf)
    r_median = np.median(rf)
    r_std = np.std(rf)
    r_hist = np.histogram(rf, bins=45)
    if show:
        print("### AGGREGATE RETURNS ### {mn} ###")
        print(f"Mean = {r_mean:5.2%}")
        print(f"Median = {r_median:5.2%}")
        print(f"StDev = {r_std:5.2%}")
        print(f"Losing start days = {r_losers:5.2%}")
        _ = plt.hist(rf, bins=45)
        plt.title("Sample Returns")
        plt.show()
    return ts, r_losers, r_mean, r_median, r_std, r_hist, mn

def plot_trend(trend, index=1):
    trend = np.array(trend)
    plt.plot(trend.T[0], trend.T[index])
    plt.ylabel("% lossy start days")
    plt.xlabel("years returns")


def model_tester(model, data, index=5, years=10, status=False):
    test_interval = datetime.timedelta(days=3)
    test_start_date = data[0][0]
    rets = []
    while test_start_date + datetime.timedelta(days=365 * years) < data[-1][0]:
        model.model_init(test_start_date, years=years)
        model.status() if status else None
        for d in data:
            model.trade(d[0], d[index])
        model.status() if status else None
        rets.append(model.returns())
        print(f"Returns = {rets[-1][1]:5.2%}") if status else None
        test_start_date += test_interval
    return rets
