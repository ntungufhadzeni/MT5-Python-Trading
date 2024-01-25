from src.interface import Trader, TradingStrategy
import MetaTrader5 as mt5


class CrossOverRobot:
    def __init__(self, volume: float, trader: Trader, strategy: TradingStrategy):
        self.volume = volume
        self.trader = trader
        self.strategy = strategy
        self.magic_number = 20240100
        self.name = 'Cross Over'
        print("Starting CrossOver Robot")

    def trade(self):
        print("Searching for trading signal")
        symbol, signal = self.strategy.signal()

        if signal == "buy":
            total_buy, _ = self.trader.get_opened_positions(symbol, mt5.ORDER_TYPE_BUY)
            if total_buy == 0:
                print(f"Buying signal detected for {symbol}")
                result = self.trader.open_position(
                    symbol,
                    self.volume,
                    mt5.ORDER_TYPE_BUY,
                    "CrossOver buy position", self.magic_number
                )
                print(f"Buy position opened: Order #{result.order}, Volume: {result.volume}, Price: {result.price}")
            total, _ = self.trader.get_opened_positions(symbol, mt5.ORDER_TYPE_SELL)
            if total > 0:
                print(f"Closing existing sell positions for {symbol}")
                self.trader.close_positions(self.name, symbol, mt5.ORDER_TYPE_BUY)
        elif signal == "sell":
            total_sell, _ = self.trader.get_opened_positions(
                symbol, mt5.ORDER_TYPE_SELL
            )
            if total_sell == 0:
                print(f"Selling signal detected for {symbol}")
                result = self.trader.open_position(
                    symbol,
                    self.volume,
                    mt5.ORDER_TYPE_SELL,
                    "CrossOver sell position", self.magic_number
                )
                print(f"Sell position opened: Order #{result.order}, Volume: {result.volume}, Price: {result.price}")
            total, _ = self.trader.get_opened_positions(symbol, mt5.ORDER_TYPE_BUY)
            if total > 0:
                print(f"Closing existing buy positions for {symbol}")
                self.trader.close_positions(self.name, symbol, mt5.ORDER_TYPE_BUY)
        elif signal is None:
            print("No trading signal found.")

        print("Waiting for the next trading signal")
        print("\n")
