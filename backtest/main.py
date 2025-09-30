import os

import backtrader as bt

from strategies.cross_over import CrossOverStrategy
from utils.data_loader import download_data_from_yahoo


def run_backtest(data_feed, strategy=CrossOverStrategy, **kwargs):
    """
    Run a backtest with the given data feed and strategy

    Args:
        data_feed (bt.feeds.DataBase): Data feed to use for the backtest
        strategy (bt.Strategy): Strategy to use for the backtest
        **kwargs: Additional arguments to pass to the strategy

    Returns:
        bt.Cerebro: Backtrader cerebro instance after running the backtest
    """
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add the data feed
    cerebro.adddata(data_feed)

    # Add the strategy
    cerebro.addstrategy(strategy, **kwargs)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # Set the commission - 0.1% per trade
    cerebro.broker.setcommission(commission=0.001)

    # Print starting portfolio value
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run the backtest
    results = cerebro.run()

    # Print final portfolio value
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Extract results
    strat = results[0]

    print('Sharpe Ratio:', strat.analyzers.sharpe.get_analysis()['sharperatio'])
    print('DrawDown:', strat.analyzers.drawdown.get_analysis()['max']['drawdown'])
    print('Return:', strat.analyzers.returns.get_analysis()['rtot'])

    trade_analysis = strat.analyzers.trades.get_analysis()

    print("==== Trade Analysis ====")
    print(f"Total Trades: {trade_analysis.get('total', {}).get('total', 0)}")
    print(f"Won: {trade_analysis.get('won', {}).get('total', 0)}")
    print(f"Lost: {trade_analysis.get('lost', {}).get('total', 0)}")

    if 'won' in trade_analysis and 'total' in trade_analysis['won'] and trade_analysis['won']['total'] > 0:
        print(f"Win Rate: {trade_analysis['won']['total'] / trade_analysis['total']['total'] * 100:.2f}%")

    # Plot the results
    cerebro.plot(style='candlestick')

    return cerebro


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('results', exist_ok=True)

    # Example 1: Using Yahoo Finance data
    print("Running backtest with Yahoo Finance data...")
    symbol = 'EURUSD=X'  # EURUSD forex pair
    start_date = '2020-01-01'
    end_date = '2023-12-31'

    # Download data
    data_feed = download_data_from_yahoo(symbol, start_date, end_date)

    # Run backtest
    cerebro = run_backtest(
        data_feed,
        strategy=CrossOverStrategy,
        ma_short_period=20,
        ma_long_period=50,
        printlog=True
    )

    # Example 2: Using local CSV data (if you have it)
    """
    print("\nRunning backtest with local CSV data...")
    data_path = os.path.join('data', 'EURUSD_H1.csv')

    # Check if the file exists
    if os.path.exists(data_path):
        # Load data
        data_feed = load_data_from_csv(data_path)

        # Run backtest
        cerebro = run_backtest(
            data_feed, 
            strategy=CrossOverStrategy, 
            ma_short_period=20,
            ma_long_period=50,
            printlog=True
        )
    else:
        print(f"CSV file {data_path} not found. Skipping this example.")
    """
