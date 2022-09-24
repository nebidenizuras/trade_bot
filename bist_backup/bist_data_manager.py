import yfinance as yf
import csv

# Write Historical Data To File
def historical_data_write_to_file(symbol, interval, data):
    fileName = symbol + "_" + interval + ".csv"
    data.to_csv(fileName)

    with open(fileName, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(fileName, 'w') as fout:
        fout.writelines(data[1:])

# Get Historical Data of Symbol
# start="2022-08-01", end="2022-08-02", interval = [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
def get_historical_data_symbol(symbol, startDateOfData, endDateOfData, interval):
    print("\nStarted Data Downloading...: " + symbol + " " + interval + " Time Frame")
    data = yf.download(symbol, start=startDateOfData, end=endDateOfData, interval = interval)

    historical_data_write_to_file(symbol, interval, data)

    print("Finished Data Downloading...")




#get_historical_data_symbol("FROTO.IS", "2022-08-22", "2022-08-29", "1m")
