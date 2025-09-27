import MetaTrader5 as mt5
import pandas as pd

from mt5_trading.adapters import TradingData


class MT5Data(TradingData):
    def __init__(self, login: str, server: str, password: str, terminal_path: str, symbol: str, time_frame: int) -> None:
        mt5.initialize()
        mt5.login(login=login, server=server, password=password, path=terminal_path)
        self.symbol = symbol
        self.time_frame = time_frame

    def get_data(self) -> pd.DataFrame:
        rates = mt5.copy_rates_from_pos(self.symbol, self.time_frame, 0, 1000)
        rates_frame = pd.DataFrame(rates)
        rates_frame["time"] = pd.to_datetime(rates_frame["time"], unit="s")
        return rates_frame

    def get_symbol(self) -> str:
        return self.symbol
