import datetime

class Model:

    name = "BuyHold"
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
        return self.start_date, ret, time_span.days / 365, self.name


class KellyModel(Model):
    name = "Kelly"

    def __init__(self, capital=10000, bond_fract=0.4, rebalance_period=90):
        self.init_capital = capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        self.init_bond_frac = bond_fract
        self.init_rebalance_period = rebalance_period

    def model_init(self, start_date, years=1):
        self.name += f"_{self.init_bond_frac:.2}_{self.init_rebalance_period}"
        self.capital = self.init_capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        #
        self.start_date = start_date
        self.end_date = start_date + datetime.timedelta(days=365 * years)
        self.first_trigger = False
        self.last_trigger = False
        #
        self.bond_frac = self.init_bond_frac
        self.stock_frac = 1 - self.bond_frac
        self.interest_rate = .02
        self.interest_factor = self.interest_rate / 365
        self.rebalance_period = datetime.timedelta(days=self.init_rebalance_period)
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

class InsuranceModel(Model):
    name = "Insurance"

    def __init__(self, capital=10000, insurance_frac=0.10, insurance_period=90, insurance_rate=-0.005, insurance_deductible=0.15):
        self.init_capital = capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        # Assume insurance covers the losses above a minimum size (deductible?)
        self.init_insurance_frac = insurance_frac  # capital allocated to insurance strategy
        self.init_insurance_period = insurance_period # period of insurance rate
        self.init_insurance_rate = insurance_rate  # insurance rate
        self.init_insurance_deductible = insurance_deductible  # insurance covers losses over this large in period

    def model_init(self, start_date, years=1):
        self.name += f"_{self.init_insurance_frac:.2}_{self.init_insurance_period}"
        self.capital = self.init_capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        #
        self.start_date = start_date
        self.end_date = start_date + datetime.timedelta(days=365 * years)
        self.first_trigger = False
        self.last_trigger = False
        #
        self.insurance_frac = self.init_insurance_frac
        self.stock_frac = 1 - self.insurance_frac
        self.insurance_rate = self.init_insurance_rate
        self.insurance_rate_factor = self.insurance_rate / 365
        self.insurance_deductible = self.init_insurance_deductible
        self.rebalance_period = datetime.timedelta(days=self.init_insurance_period)
        self.last_rebalance = self.start_date
        self.last_price = []   # list of prices for losses days
        self.losses_days = 10  # number of days to calculate losses

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
            self.capital *= (1. - self.insurance_rate_factor) ** ((date - self.last_rebalance).days)  # insurance payment
            stock_value = self.shares * price             # current stock value
            total_capital = self.capital + stock_value
            delta_shares = self.stock_frac * total_capital / price - self.shares
            self.capital -= delta_shares * price   # rebalance
            self.shares += delta_shares
            self.trades.append((date, price, delta_shares, self.capital, self.shares))
            self.last_rebalance = date
        else:
            delta_shares = 0

        if len(self.last_price) < self.losses_days:
            self.last_price.append(price)
        else:
            start_price = self.last_price.pop(0)
            loss = (price - start_price) / start_price
            if loss < -self.insurance_deductible:
                # insurance pays out
                self.capital -= self.capital * loss
                self.trades.append((date, price, 0, self.capital, self.shares))
                self.last_price = [price]
            else:
                self.last_price.append(price)

        return

