import datetime
import multiprocessing as mp
import csv
from itertools import repeat

from returns.data import *
from returns.models import *

path = "./out_data/"

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

def model_test_manager(years, date_str):
    d, h = get_data()
    index = 5
    for i in [0.2, 0.6]:
        for j in [90, 180]:
            m = KellyModel(bond_fract=i, rebalance_period=j)
            rets = model_tester(m, d, index=index, years=years, status=False)
            fn = f"{path}returns_{years}_{rets[0][3]}_{date_str}.csv"
            with open(fn, "w") as outfile:
                writer = csv.writer(outfile)
                writer.writerow(["date", "return", "time_span", "model_name"])
                for r in rets:
                    writer.writerow(r)

if __name__ == '__main__':
    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    p = mp.Pool()
    args = zip(range(1,16), repeat(date_str))
    p.starmap(model_test_manager, args)


