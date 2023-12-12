import datetime
import multiprocessing as mp
import csv
from itertools import repeat

from returns.data import *
from returns.models import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(process)d %(asctime)s %(levelname)s %(funcName)20s() %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='app.log',
                    filemode='w')

path = "./out_data/"

def model_tester(model, data, years=10, status=False):
    """
    Tests the given model on the provided data for the specified number of years.
    """
    test_interval = datetime.timedelta(days=3)
    test_start_date = data[0][0]
    rets = []

    logging.info("Starting model testing")

    while test_start_date + datetime.timedelta(days=365 * years) < data[-1][0]:
        model.model_config(test_start_date, years=years)

        if status:
            model.status()
            logging.debug("Model status checked")

        for d in data:
            _data = (d[combined_sp500_index], d[combined_interest_index])
            model.trade(d[0], _data)

        if status:
            model.status()
            logging.debug("Model status checked after trading")

        rets.append(model.total_returns())
        if status:
            logging.info(f"Returns = {rets[-1][1]:5.2%}")
        test_start_date += test_interval

    logging.info("Model testing completed")
    return rets

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

    for m in model_generator2():
        rets = model_tester(m, d, years=years, status=False)

        fn = f"{path}returns_{years}_{rets[0][3]}_{date_str}.csv"
        logging.info(f"Writing results to {fn}")

        with open(fn, "w") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["date", "return", "time_span", "model_name"])
            for r in rets:
                writer.writerow(r)

if __name__ == '__main__':
    # date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    date_str = "2023-09-29_0000"
    p = mp.Pool()
    args = zip(range(1, 16), repeat(date_str))
    p.starmap(model_test_manager, args)


