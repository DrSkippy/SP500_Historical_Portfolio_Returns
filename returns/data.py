import csv
import datetime
import locale

locale.setlocale(locale.LC_ALL, '')

sp500path = "./data/SP500.tab"
FMT_IN = "%b %d, %Y"
FMT_out = "%Y-%m-%d"
index = 5


def get_data():
    data = []
    with open(sp500path, "r") as infile:
        reader = csv.reader(infile, delimiter="\t")
        first = True
        for row in reader:
            if first:
                first = False
                header = row
            else:
                date = datetime.datetime.strptime(row[0], FMT_IN)
                row_data = [locale.atof(x) for x in row[1:]]
                data.append([date] + row_data)
    data = sorted(data)
    print(f"Path = {sp500path}")
    print(f"Read {len(data)} rows")
    print(f"Fields = {header}")
    return data, header


def get_model_run(suffix, years=[1,2,3,4]):
    res = {}
    for y in years:
        fn = f"../out_data/returns_{y}_{suffix}"
        print(f"Reading {fn}")
        data = []
        with open(fn, "r") as infile:
            reader = csv.reader(infile)
            first = True
            for row in reader:
                if first:
                    first = False
                    header = row
                else:
                    date = datetime.datetime.strptime(row[0][:10], FMT_out)
                    data.append([date] + row[1:])
        res[y] = sorted(data)
        print(f"Read {len(data)} rows")
        print(f"Fields = {header}")
    return res, header