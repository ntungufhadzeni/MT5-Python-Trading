import talib
import pandas as pd

from mt5_trading.adapters import TradingStrategy, TradingData
from mt5_trading.domain.signal import Signal


class CrossOverStrategy(TradingStrategy):
    def __init__(self, trading_data: TradingData) -> None:
        self.data = trading_data

    def signal(self) -> tuple[str, Signal]:
        df: pd.DataFrame = self.data.get_data()
        df["MA20"] = df["close"].rolling(window=20).mean()
        df["MA50"] = df["close"].rolling(window=50).mean()

        df["macd"], df["signal"], _ = talib.MACD(df["close"])

        buy_condition = df["MA20"] > df["MA50"]
        sell_condition = df["MA20"] < df["MA50"]

        last_buy = bool(buy_condition.iloc[-1])
        last_sell = bool(sell_condition.iloc[-1])

        symbol = self.data.get_symbol()
        if last_buy and not last_sell:
            return symbol, Signal.BUY
        if last_sell and not last_buy:
            return symbol, Signal.SELL
        return symbol, Signal.NONE

