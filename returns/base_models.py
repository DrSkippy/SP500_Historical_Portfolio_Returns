import datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def returns(start, end):
    delta = end[1] - start[1]
    delta_frac = delta / start[1]
    return end[0], delta, delta_frac


def historical_returns(data, return_delta, index):
    history = []
    return_data = []
    for d in data:
        history.append([d[0], d[index]])
        if d[0] >= history[0][0] + return_delta:
            data_from = history.pop(0)
            return_data.append(returns(data_from, history[-1]))
    return return_data


def all_time_returns(data, n=20, index=5):
    trend = []
    for years in range(1, n):
        print("#" * 40)
        return_delta = datetime.timedelta(days=365 * years)
        return_data = historical_returns(data, return_delta, index)
        df = pd.DataFrame(return_data, columns=["Date", "Return", "Return Frac"])
        print(f"Distribution over {years} years returns")
        dfd = pd.DataFrame({"Return Frac": df["Return Frac"].describe()})
        print(dfd)
        r = len(df[df['Return Frac'] < 0.0]) / len(return_data) * 100
        trend.append([years, r])
        print(f"Losing start days = {r:5.2f}%")
        print(f"Mean = {df['Return Frac'].mean():5.2f}%")
        print(f"Median = {df['Return Frac'].median():5.2f}%")
        df.hist(column="Return Frac", bins=45)
        plt.show()
    return trend


def plot_trend(trend):
    trend = np.array(trend)
    plt.plot(trend.T[0], trend.T[1])
    plt.ylabel("% lossy start days")
    plt.xlabel("years returns")
