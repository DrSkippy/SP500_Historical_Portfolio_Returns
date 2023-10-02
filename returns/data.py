import csv
import datetime
import locale

locale.setlocale(locale.LC_ALL, '')

sp500path = "../data/SP500.tab"
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
