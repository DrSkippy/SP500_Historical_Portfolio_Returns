import datetime
import multiprocessing
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Model:

    def __init__(self, capital=10000):
        self.init_capital = capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)

    def model_init(self, start_date, years=1):
        self.capital = self.init_capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        #
        self.start_date = start_date
        self.end_date = start_date + datetime.timedelta(days=365 * years)
        self.first_trigger = False
        self.last_trigger = False

    def trade(self, date, price):
        if date >= self.start_date and not self.first_trigger:
            delta_shares = self.capital / price
            self.first_trigger = True
        elif date >= self.end_date and not self.last_trigger:
            delta_shares = -self.shares
            self.last_trigger = True
        else:
            delta_shares = 0
        if delta_shares != 0:
            self.shares += delta_shares
            self.capital -= delta_shares * price
            self.trades.append((date, price, delta_shares, self.capital, self.shares))
        return

    def status(self):
        print("### STATUS ###")
        print(f"Initial Capital = {self.init_capital:10.2f}")
        print(f"Capital = {self.capital:10.2f}")
        print(f"Shares = {self.shares:10.2f}")
        for x in self.trades:
            print(f"{x[0]} {x[1]:10.2f} {x[2]:10.2f} {x[3]:10.2f} {x[4]:10.2f}")

    def returns(self):
        time_span = self.trades[-1][0] - self.trades[0][0]
        ret = (self.capital - self.init_capital) / self.init_capital
        return self.start_date, ret, time_span.days / 365


class MixedModel(Model):

    def model_init(self, start_date, years=1):
        self.capital = self.init_capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        #
        self.start_date = start_date
        self.end_date = start_date + datetime.timedelta(days=365 * years)
        self.first_trigger = False
        self.last_trigger = False
        #
        self.bond_frac = .4
        self.stock_frac = 1 - self.bond_frac
        self.interest_rate = .02
        self.interest_factor = self.interest_rate / 365
        self.rebalance_period = datetime.timedelta(days=90)
        self.last_rebalance = self.start_date

    def trade(self, date, price):
        if date >= self.start_date and not self.first_trigger:
            self.shares = self.stock_frac * self.capital / price  # start by buying stocks
            self.capital -= self.shares * price  # reduce cash capital by the stock purchase
            self.first_trigger = True
            self.trades.append((date, price, self.shares, self.capital, self.shares))
        elif date >= self.end_date and not self.last_trigger:
            self.capital += self.shares * price  # sell all stocks
            self.shares = 0
            self.last_trigger = True
            self.trades.append((date, price, -self.shares, self.capital, self.shares))
        elif date >= self.last_rebalance + self.rebalance_period and self.first_trigger and not self.last_trigger:
            self.capital *= (1. + self.interest_factor) ** ((date - self.last_rebalance).days)  # interest on cash
            stock_value = self.shares * price  # current stock value
            total_capital = self.capital + stock_value
            delta_shares = self.stock_frac * total_capital / price - self.shares
            self.capital -= delta_shares * price
            self.shares += delta_shares
            self.trades.append((date, price, delta_shares, self.capital, self.shares))
            self.last_rebalance = date
        else:
            delta_shares = 0
        return


def agg_returns(return_data, show=True):
    df = pd.DataFrame(return_data, columns=["Date", "Return Frac", "Time Span"])
    df["Time Span"] = df["Time Span"].astype(int)
    df["Return Frac"] = df["Return Frac"].astype(float)
    dfd = pd.DataFrame({"Return Frac": df["Return Frac"].describe()})
    print(dfd) if show else None
    r_losers = len(df[df['Return Frac'] < 0.0]) / len(return_data)
    print(f"Losing start days = {r_losers:5.2%}") if show else None
    print(f"Mean = {df['Return Frac'].mean():5.2%}") if show else None
    print(f"StDev = {df['Return Frac'].std():5.2%}") if show else None
    print(f"Median = {df['Return Frac'].median():5.2%}") if show else None
    if show:
        df.hist(column="Return Frac", bins=45)
        plt.show()
    return df["Time Span"][0], r_losers


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
