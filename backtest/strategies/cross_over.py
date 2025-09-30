import backtrader as bt
import pandas as pd
import numpy as np


class CrossOverStrategy(bt.Strategy):
    """
    A Backtrader implementation of the CrossOver strategy.

    This strategy generates buy signals when the 20-period moving average crosses above
    the 50-period moving average, and sell signals when the 20-period moving average
    crosses below the 50-period moving average.
    """

    params = (
        ('ma_short_period', 20),
        ('ma_long_period', 50),
        ('printlog', False),
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # Create the moving average indicators
        self.ma_short = bt.indicators.SimpleMovingAverage(
            self.dataclose, period=self.params.ma_short_period
        )
        self.ma_long = bt.indicators.SimpleMovingAverage(
            self.dataclose, period=self.params.ma_long_period
        )

        # Add MACD indicator
        self.macd = bt.indicators.MACD(
            self.dataclose,
            period_me1=12,
            period_me2=26,
            period_signal=9
        )

        # To keep track of pending orders
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a CrossOver indicator
        self.crossover = bt.indicators.CrossOver(self.ma_short, self.ma_long)

    def log(self, txt, dt=None, doprint=False):
        """Logging function"""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, '
                    f'Comm: {order.executed.comm:.2f}'
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, '
                    f'Comm: {order.executed.comm:.2f}'
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'OPERATION PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')

    def next(self):
        # Log the closing price of the series
        self.log(f'Close: {self.dataclose[0]:.2f}')

        # Check if an order is pending
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet in market, look for buy signal
            if self.crossover > 0:  # if ma_short crosses above ma_long
                self.log('BUY CREATE, {:.2f}'.format(self.dataclose[0]))
                self.order = self.buy()  # Keep track of the created order

        else:
            # Already in market, look for sell signal
            if self.crossover < 0:  # if ma_short crosses below ma_long
                self.log('SELL CREATE, {:.2f}'.format(self.dataclose[0]))
                self.order = self.sell()  # Keep track of the created order

    def stop(self):
        self.log('MA Short Period: {}, MA Long Period: {}'.format(
            self.params.ma_short_period, self.params.ma_long_period
        ), doprint=True)
        self.log('(MA Strategy) Ending Value: %.2f' % self.broker.getvalue(), doprint=True)
