import csv
import datetime
import logging
import multiprocessing as mp
from itertools import repeat

from returns.data import *
from returns.models import *

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(process)d|%(asctime)s|%(levelname)s|%(funcName)20s()|%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='app.log',
                    filemode='w')

path = "./out_data/"


def model_tester(model, data, years=10):
    """
    Tests the given model on the provided data for the specified number of years.
    """
    test_interval = datetime.timedelta(days=STRIDE_DAYS)
    test_start_date = data[0][0] # first (oldest) date in data
    model_returns = []

    logging.info("Starting model testing")

    while test_start_date + datetime.timedelta(days=365 * years) < data[-1][0]:
        model.model_config(test_start_date, years=years)

        skip_to_date = test_start_date - PADDING_TIME_DELTA
        for d in data:
            if skip_to_date is not None and d[0] < skip_to_date:
                continue
            else:
                # data is (stock price, interest rate by years)
                _data = (d[combined_sp500_index], d[combined_interest_index])
                skip_to_date = model.trade(d[0], _data)

        for log_line in model.status():
            logging.debug(log_line)

        model_returns.append(model.total_returns())
        logging.debug((f"frac_returns={model_returns[-1][1]:5.2%} yearly_return_rate={model_returns[-1][2]}"
                       "model={model.name} start_date={test_start_date}"))
        test_start_date += test_interval

    logging.info("End model testing")
    return model_returns


def model_generator():
    """
    Generates models for testing.
    """
    for i in [0.1, 0.2, 0.3, 0.4, 0.5]:
        for j in [90, 180]:
            logging.debug(f"Testing KellyModel with bond_fract={i}, rebalance_period={j}")
            yield KellyModel(bond_fract=i, rebalance_period=j)


def model_generator2():
    """
    Generates models for testing.
    """
    logging.debug(f"Testing Buy and Hold Model")
    yield Model()


def model_test_manager(years, date_str):
    """
    Manages the testing of models for the specified years.
    """
    logging.info(f"Testing models for {years} years")
    d, h = get_combined_data()

    for m in model_generator():
        rets = model_tester(m, d, years=years)

        fn = f"{path}returns_{years}_{rets[0][-1]}_{date_str}.csv"
        logging.info(f"Writing results to {fn}")

        with open(fn, "w") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["date",
                             "frac_return",
                             "yearly_return_rate",
                             "time_span",
                             "model_name"])
            for r in rets:
                writer.writerow(r)


if __name__ == '__main__':
    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    p = mp.Pool()
    args = zip(range(1, 16), repeat(date_str))
    p.starmap(model_test_manager, args)
    logger.info("################ All model testing completed ################")
