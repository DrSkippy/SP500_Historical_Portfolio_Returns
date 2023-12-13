import datetime
import multiprocessing
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from returns.models import *


def aggregate_returns(returns_data, show=False):
    """
    returns_data = ["date",
                    "frac_return",
                    "yearly_return_rate",
                    "time_span",
                    "model_name"]
    """
    returns_data_vectors = np.array(returns_data).T
    # get values of first line
    time_span = round(returns_data_vectors[3].astype(float)[0],0)
    model_name = returns_data_vectors[-1][0]
    # vectors of returns
    total_returns = returns_data_vectors[1].astype(float)
    yearly_compounded_returns = returns_data_vectors[2].astype(float)
    # calculated stats
    fraction_losing_starts = np.count_nonzero(total_returns < 0.0) / len(total_returns)
    mean_total_returns = np.mean(total_returns)
    mean_yearly_compound_returns = np.mean(yearly_compounded_returns)
    median_total_returns = np.median(total_returns)
    sdev_total_returns = np.std(total_returns)
    r_hist = np.histogram(total_returns, bins=45)
    mode_total_returns = r_hist[1][np.argmax(r_hist[0])-1]
    if show:
        print(f"### AGGREGATE RETURNS ### {model_name} ###")
        print(f"Time span         = {time_span:5.1f} years")
        print(f"Avg Yearly Return = {mean_yearly_compound_returns:5.2%}")
        print(f"Mean Returns      = {mean_total_returns:5.2%}")
        print(f"Median Returns    = {median_total_returns:5.2%}")
        print(f"Mode of Returns   = {mode_total_returns:5.2%}")
        print(f"StDev of Returns  = {sdev_total_returns:5.2%}")
        print(f"Losing start days = {fraction_losing_starts:5.2%}")
        _ = plt.hist(total_returns, bins=45)
        plt.title("Sample Returns")
        plt.show()
    return (time_span,
            fraction_losing_starts,
            mean_yearly_compound_returns,
            mean_total_returns,
            median_total_returns,
            mode_total_returns,
            sdev_total_returns,
            model_name)


def plot_trend(trend, index=1, title="% losing start days", trend2=None):
    _trend = np.array(trend).T[:index + 1]
    plt.plot(_trend[0].astype(float), _trend[index].astype(float))
    plt.ylabel(title)
    plt.xlabel("years returns")
    if trend2 is not None:
        _trend2 = np.array(trend2).T[:index + 1]
        plt.plot(_trend2[0].astype(float), _trend2[index].astype(float))
    plt.legend()
    plt.show()

def plot_df(df, column="fraction_losing_starts"):
    ax = df.plot("time_span", column, figsize=(15, 8))
    ax.set_ylabel(column)
    ax.set_xlabel("period (years)")
    plt.show()

def get_aggregate_returns_by_period(data):
    returns_stats_by_period = []
    for k, v in data.items():
        returns_stats_by_period.append(aggregate_returns(v, show=True))
    df = pd.DataFrame(returns_stats_by_period,
                      columns=["time_span",
                               "fraction_losing_starts",
                               "mean_yearly_compound_returns",
                               "mean_total_returns",
                               "median_total_returns",
                               "mode_total_returns",
                               "sdev_total_returns", "model_name"])
    df = df.sort_values(by=["time_span"])
    return returns_stats_by_period, df
