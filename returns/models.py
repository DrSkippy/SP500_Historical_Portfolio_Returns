import datetime
import logging
import math

logger = logging.getLogger(__name__)


class Model:
    model_name = "Buy&Hold"

    def __init__(self, capital=10000):
        self.init_capital = capital
        logger.info("Model initialized, but not configured")

    def model_config(self, start_date, years=1):
        self.capital = self.init_capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        #
        self.start_date = start_date
        self.end_date = start_date + datetime.timedelta(days=365 * years)
        logger.info(f"Model configured with starting capital = {self.capital}")
        logger.info(f"Model configured start date = {start_date}")
        logger.info(f"Model configured for {years} years")
        #
        self.first_trigger = True
        self.last_trigger = True

    def first_trade(self, date, price):
        # buy all shares
        self.shares = self.capital / price[0]
        self.capital -= self.shares * price[0]
        self.trades.append((date, price, self.shares, self.capital, self.shares))

    def last_trade(self, date, price):
        # sell all shares
        self.capital += self.shares * price[0]
        self.shares = 0
        self.trades.append((date, price, -self.shares, self.capital, self.shares))

    def daily_trade(self, date, price):
        # hold all shares
        pass

    def trade(self, date, price):
        potential_trade = True
        if date >= self.start_date <= date <= self.end_date:
            # inside the trading window
            logger.info(f"In trading window on {date}")
            if self.first_trigger:
                logger.info("First trade ({date})")
                self.first_trigger = False
                self.first_trade(date, price)
            else:
                # inside the trading window, but not first or last
                self.daily_trade(date, price)
        elif date > self.end_date and self.last_trigger:
            logger.info("Last trade ({date})")
            self.last_trigger = False
            self.last_trade(date, price)
        else:
            potential_trade = False

        if potential_trade:
            logger.info(
                f"After trading on {date}: ${self.capital} and {self.shares} shares")
        return

    def status(self):
        print("#### STATUS ####")
        print(f"Initial Capital = {self.init_capital:10.2f}")
        print(f"Capital = {self.capital:10.2f}")
        print(f"Shares = {self.shares:10.2f}")
        print(f"Trades = {len(self.trades)}:")
        for x in self.trades:
            print(f"{x[0]} {x[1]:10.2f} {x[2]:10.2f} {x[3]:10.2f} {x[4]:10.2f}")

    def yearly_returns(self, total_returns, period_years):
        # Estimate the yearly compounding rate from total returns
        return math.exp(math.log(total_returns) / period_years) - 1.

    def total_returns(self):
        time_span = self.trades[-1][0] - self.trades[0][0]
        returns = (self.capital - self.init_capital) / self.init_capital
        yrl_ret = self.yearly_returns(returns, time_span.days/365)
        return self.start_date, returns, yrl_ret, time_span.days/365, self.model_name


class KellyModel(Model):
    model_name = "Fractional_Kelly"

    def __init__(self, capital=10000, bond_fract=0.4, rebalance_period=90):
        self.init_capital = capital
        self.init_bond_frac = bond_fract
        self.init_rebalance_period = rebalance_period
        logger.info("Model initialized, but not configured")

    def model_config(self, start_date, years=1):
        self.model_name += f"_{self.init_bond_frac:.2}_{self.init_rebalance_period}"
        self.capital = self.init_capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        #
        self.start_date = start_date
        self.end_date = start_date + datetime.timedelta(days=365 * years)
        logger.info(f"Model configured with starting capital = {self.capital}")
        logger.info(f"Model configured start date = {start_date}")
        logger.info(f"Model configured for {years} years")
        #
        self.first_trigger = True
        self.last_trigger = True
        #
        self.bond_frac = self.init_bond_frac
        self.stock_frac = 1. - self.bond_frac
        self.rebalance_period = datetime.timedelta(days=self.init_rebalance_period)
        self.last_rebalance = self.start_date
        logger.info(f"Model configured with bond fraction = {self.bond_frac}")
        logger.info(f"Model configured with re-balance period = {self.rebalance_period}")

    def first_trade(self, date, price):
        self.shares = self.stock_frac * self.capital / price[0]  # start by buying stocks
        self.capital -= self.shares * price[0]  # reduce cash capital by the stock purchase
        self.first_trigger = True
        self.trades.append((date, price, self.shares, self.capital, self.shares))

    def last_trade(self, date, price):
        self.capital += self.shares * price[0]  # sell all stocks
        self.shares = 0
        self.last_trigger = True
        self.trades.append((date, price, -self.shares, self.capital, self.shares))

    def daily_trade(self, date, price):
        # Only trade if rebalance period has passed
        if date >= self.last_rebalance + self.rebalance_period:
            self.rebalanc(date, price)

    def rebalance(self, date, price):
        # interest on capital, compound daily
        logger.info(f"Trading to re-balance on {date}")
        interest_factor = price[1] / 365
        self.capital *= (1. + interest_factor) ** ((date - self.last_rebalance).days)
        # current stock value
        stock_value = self.shares * price[0]
        # daily total capital
        total_capital = self.capital + stock_value
        delta_shares = self.stock_frac * total_capital / price[0] - self.shares
        self.capital -= delta_shares * price[0]
        self.shares += delta_shares
        self.trades.append((date, price, delta_shares, self.capital, self.shares))
        self.last_rebalance = date


class InsuranceModel(KellyModel):
    model_name = "Insurance"

    def __init__(self, capital=10000, insurance_frac=0.10, insurance_period=90, insurance_rate=-0.005,
                 insurance_deductible=0.15):
        self.init_capital = capital
        # Assume insurance covers the losses above a minimum size (deductible?)
        self.init_insurance_frac = insurance_frac  # capital allocated to insurance strategy
        self.init_insurance_period = insurance_period  # period of insurance rate
        self.init_insurance_rate = insurance_rate  # insurance rate
        self.init_insurance_deductible = insurance_deductible  # insurance covers losses over this large in period

    def model_config(self, start_date, years=1):
        self.name += f"_{self.init_insurance_frac:.2}_{self.init_insurance_period}"
        self.capital = self.init_capital
        self.shares = 0
        self.trades = []  # list of tuples (date, price, shares)
        #
        self.start_date = start_date
        self.end_date = start_date + datetime.timedelta(days=365 * years)
        logger.info(f"Model configured with starting capital = {self.capital}")
        logger.info(f"Model configured start date = {start_date}")
        logger.info(f"Model configured for {years} years")
        #
        self.first_trigger = True
        self.last_trigger = True
        #
        self.insurance_frac = self.init_insurance_frac
        self.stock_frac = 1 - self.insurance_frac
        self.insurance_rate = self.init_insurance_rate
        self.insurance_deductible = self.init_insurance_deductible
        self.rebalance_period = datetime.timedelta(days=self.init_insurance_period)
        self.last_rebalance = self.start_date
        self.last_price = []  # list of prices for losses days
        self.losses_days = 10  # number of days to calculate losses
        logger.info(f"Model configured with insurance fraction = {self.insurance_frac}")
        logger.info(f"Model configured with insurance rate = {self.insurance_rate}")
        logger.info(f"Model configured with insurance deductible = {self.insurance_deductible}")
        logger.info(f"Model configured with re-balance period = {self.rebalance_period}")

    def daily_trade(self, date, price):
        payout = False
        # Loss insurance triggered?
        if len(self.last_price) < self.losses_days:
            # Not enough history to judge loss for payoff
            self.last_price.append(price)
        else:
            start_price = self.last_price.pop(0)
            loss = (price - start_price) / start_price
            if loss < -self.insurance_deductible:
                payout = True
                # insurance pays out
                self.capital -= self.capital * loss
                self.trades.append((date, price, 0, self.capital, self.shares))
                self.last_price = [price]
            else:
                self.last_price.append(price)

        if date >= self.last_rebalance + self.rebalance_period and not payout:
            _price = (price, -self.insurance_rate)
            self.rebalance(date, _price)
