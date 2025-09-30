import os
import backtrader as bt
import pandas as pd
import datetime as dt
import yfinance as yf


def load_data_from_csv(file_path, date_format='%Y-%m-%d'):
    """
    Load data from a CSV file into a Backtrader data feed

    Args:
        file_path (str): Path to the CSV file
        date_format (str): Format of the date column in the CSV

    Returns:
        bt.feeds.PandasData: Backtrader data feed
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")

    # Load the data from the CSV file
    df = pd.read_csv(file_path, parse_dates=True)

    # Convert the date column to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], format=date_format)
            df.set_index('date', inplace=True)
        elif 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], format=date_format)
            df.set_index('datetime', inplace=True)

    # Create a Backtrader data feed
    data_feed = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # None if the index is the datetime
        open=0,  # Column index for the open price
        high=1,  # Column index for the high price
        low=2,  # Column index for the low price
        close=3,  # Column index for the close price
        volume=4,  # Column index for the volume
        openinterest=-1  # -1 if no open interest column
    )

    return data_feed


def download_data_from_yahoo(symbol, start_date, end_date, timeframe='1d'):
    """
    Download data from Yahoo Finance

    Args:
        symbol (str): Symbol to download data for
        start_date (str or datetime): Start date in format 'YYYY-MM-DD'
        end_date (str or datetime): End date in format 'YYYY-MM-DD'
        timeframe (str): Timeframe for the data (default: '1d')

    Returns:
        bt.feeds.PandasData: Backtrader data feed
    """
    # Convert string dates to datetime if needed
    if isinstance(start_date, str):
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

    # Download data from Yahoo Finance
    data = yf.download(symbol, start=start_date, end=end_date, interval=timeframe)
    data_single_level = data.copy()
    data_single_level.columns = data_single_level.columns.droplevel(1)  # Drop the ticker level

    # Create a Backtrader data feed
    data_feed = bt.feeds.PandasData(dataname=data_single_level)

    return data_feed
