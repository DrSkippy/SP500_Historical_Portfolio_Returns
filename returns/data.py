import csv
import datetime
import locale
import logging
import sys

logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, '')

sp500path = "./data/SP500.tab"
interestpath = "./data/interest.tab"

FMT_IN = "%b %d, %Y"
FMT_out = "%Y-%m-%d"

sp500_index = 5
interest_index = 1
combined_sp500_index = sp500_index
combined_interest_index = 6 + interest_index


def get_combined_data():
    """
    Reads S&P 500 and interest data from TSV files.

    Returns:
    tuple: A tuple containing the combined data (with dates and values) and
    the header.
    """
    result = []
    sp500, sp500_header = get_sp500()
    interest, interest_header = get_interest()
    # Append rows from interest data to S&P 500 data
    for i, row in enumerate(sp500):
        result.append(row + interest[row[0].year])
    return result, sp500_header + interest_header


def get_interest():
    """
    Reads interest data from a TSV file.

    Returns:
    tuple: A tuple containing the interest data (as a dictionary with years as keys) and the header.
    """
    interest_data = {}

    with open(interestpath, "r") as infile:
        reader = csv.reader(infile, delimiter="\t")
        header = next(reader)[1:]  # Reading the header

        for row in reader:
            year = int(row[0])
            interest_data[year] = [float(x.strip('%')) / 100. for x in row[1:]]

    # Debugging information
    logger.info(f"Reading interest data")
    logger.info(f"Path = {interestpath}")
    logger.info(f"Read {len(interest_data)} rows")
    logger.info(f"Fields = {header}")

    return interest_data, header


def get_sp500():
    """
    Reads S&P 500 data from a TSV file.

    Returns:
    tuple: A tuple containing the sorted data (with dates and values) and the header.
    """
    parsed_data = []

    with open(sp500path, "r") as infile:
        reader = csv.reader(infile, delimiter="\t")
        header = next(reader)  # Reading the header

        for row in reader:
            # Parse date and data values
            date = datetime.datetime.strptime(row[0], FMT_IN)
            row_data = [locale.atof(x) for x in row[1:]]
            parsed_data.append([date] + row_data)

    # Sort data by date
    parsed_data.sort()

    # Debugging information
    logger.info(f"Reading S&P 500 data")
    logger.info(f"Path = {sp500path}")
    logger.info(f"Read {len(parsed_data)} rows")
    logger.info(f"Fields = {header}")

    return parsed_data, header


def get_model_run(suffix, years=[1, 2, 3, 4]):
    """
    Reads data from CSV files for specified years and returns the data along with headers.

    Parameters:
    suffix (str): Suffix for the filename.
    years (list): List of years for which to read the data.

    Returns:
    tuple: A dictionary containing data for each year and the header of the CSV files.
    """
    results = {}
    header = None

    logger.info(f"Reading model run data")
    for year in years:
        filename = f"../out_data/returns_{year}_{suffix}"
        print(f"Reading {filename}")

        with open(filename, "r") as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Reading the header

            # Process each row
            data = []
            for row in reader:
                date = datetime.datetime.strptime(row[0][:10], FMT_out)
                data.append([date] + row[1:])

        results[year] = sorted(data)
        logger.info(f"Read {len(data)} rows")
        logger.info(f"Fields = {header}")

    return results, header


def select_file(files):
    """
    Prompts the user to select a file suffix from a list of file names.

    Parameters:
    files (list of str): A list of file names.

    Returns:
    str: The selected file suffix.
    """
    # Extract unique suffixes from file names
    suffixes = list(set("_".join(filename.split("_")[2:]) for filename in files))
    logger.info("Suffixes extracted from file names")

    # Display the suffixes with indices
    for i, suffix in enumerate(suffixes):
        print(f"{i} - {suffix}")

    # User input with error handling
    while True:
        try:
            selected_index = int(input("Choose a number: "))
            if 0 <= selected_index < len(suffixes):
                selected_suffix = suffixes[selected_index]
                logger.info(f"User selected index: {selected_index}")
                break
            else:
                logger.warning("User selected an invalid number outside the range")
                print("Invalid number. Please try again.")
        except ValueError:
            logger.error("Invalid input, not a number")
            print("Invalid input. Please enter a number.")

    logger.info(f"User selected suffix: {selected_suffix}")
    return selected_suffix


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        stream=sys.stdout,
                        filemode="w")

    # Read data
    data, header = get_combined_data()

    # Write data to a CSV file
    with open("./data/combined_data.csv", "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        for row in data:
            writer.writerow(row)
