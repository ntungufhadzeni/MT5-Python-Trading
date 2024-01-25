import MetaTrader5 as mt5
import pandas as pd
import talib

from .interface import Trader, TradingStrategy, TradingData


class MT5Trader(Trader):
    """
        MT5Trader class for executing trading operations using MetaTrader 5.

        Methods:
            - open_position(symbol, volume, position_type, comment, magic_number, sl=None, tp=None): Open a trading position.
            - close_positions(robot_name: str, symbol=None, position_type=None): Close trading positions.
            - get_opened_positions(symbol=None, position_type=None): Get information about opened positions.
            - get_all_positions(): Get information about all positions.
            - send_to_break_even(df: pd.DataFrame, percentage: float): Adjust stop-loss to break-even based on a percentage.
            - calculate_position_size(symbol, stop_loss, per_to_risk): Calculate position size based on risk parameters.

        Example usage:
        ```
        mt5_trader = MT5Trader()
        mt5_trader.open_position(symbol='EURUSD', volume=0.1, position_type=mt5.ORDER_TYPE_BUY,
                                 comment='Example position', magic_number=202204)
        mt5_trader.close_positions(robot_name='MyRobot', symbol='EURUSD', position_type=mt5.ORDER_TYPE_SELL)
        opened_positions = mt5_trader.get_opened_positions(symbol='EURUSD', position_type=mt5.ORDER_TYPE_BUY)
        all_positions = mt5_trader.get_all_positions()
        mt5_trader.send_to_break_even(opened_positions, percentage=0.5)
        position_size = mt5_trader.calculate_position_size(symbol='EURUSD', trade_info=1.0800, per_to_risk=0.02)
        ```
        """

    def open_position(self, symbol, volume, position_type, comment, magic_number, sl=None, tp=None):
        """
            Open a trading position.

            Args:
                - symbol (str): Trading symbol (e.g., 'EURUSD').
                - volume (float): Trading volume.
                - position_type: Type of position (e.g., mt5.ORDER_TYPE_BUY or mt5.ORDER_TYPE_SELL).
                - comment (str): Comment for the position.
                - magic_number (int): Magic number associated with the position.
                - sl (float): Stop-loss value.
                - tp (float): Take-profit value.

            Returns:
                OrderSendResult: Information about the result of the order send operation.
        """
        if not sl and not tp:
            order = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": position_type,
                "magic": magic_number,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            return mt5.order_send(order)
        elif not sl and tp:
            order = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "tp": tp,
                "volume": volume,
                "type": position_type,
                "comment": comment,
                "magic": magic_number,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            return mt5.order_send(order)
        elif sl and not tp:
            order = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "sl": sl,
                "volume": volume,
                "type": position_type,
                "comment": comment,
                "magic": magic_number,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            return mt5.order_send(order)
        elif sl and tp:
            order = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "sl": sl,
                "tp": tp,
                "volume": volume,
                "type": position_type,
                "magic": magic_number,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            return mt5.order_send(order)

    def close_positions(self, robot_name: str, symbol=None, position_type=None):
        """
            Close trading positions.

            Args:
                - robot_name (str): Name of the robot initiating the operation.
                - symbol (str): Trading symbol (e.g., 'EURUSD'). If None, applies to all symbols.
                - position_type: Type of position (e.g., mt5.ORDER_TYPE_BUY or mt5.ORDER_TYPE_SELL). If None, applies to all positions.
        """
        df_open_positions = self.get_all_positions()

        if not df_open_positions.empty:
            if not symbol and position_type is None:
                position_list = df_open_positions["ticket"].unique().tolist()
            elif symbol and position_type is None:
                df_open_positions = df_open_positions[
                    df_open_positions["symbol"] == symbol
                    ]
                position_list = df_open_positions["ticket"].unique().tolist()
            else:
                df_open_positions = df_open_positions[
                    (df_open_positions["symbol"] == symbol) & (df_open_positions["type"] == position_type)
                    ]
                position_list = df_open_positions["ticket"].unique().tolist()

            for position in position_list:
                df_position = df_open_positions[df_open_positions["ticket"] == position]
                price_close = mt5.symbol_info_tick(df_position["symbol"].item()).bid
                type_position = df_position["type"].item()
                symbol_position = df_position["symbol"].item()
                volume_position = df_position["volume"].item()
                # 1 Sell / 0 Buy
                if type_position == 1:
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol_position,
                        "volume": volume_position,
                        "type": mt5.ORDER_TYPE_BUY,
                        "position": position,
                        "price": price_close,
                        "comment": f"{robot_name} closed position",
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }

                    mt5.order_send(close_request)
                if type_position == 0:
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol_position,
                        "volume": volume_position,
                        "type": mt5.ORDER_TYPE_SELL,
                        "position": position,
                        "price": price_close,
                        "comment": f"{robot_name} closed position",
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }

                    mt5.order_send(close_request)

    def get_opened_positions(self, symbol=None, position_type=None):
        """
            Get information about opened positions.

            Args:
                - symbol (str): Trading symbol (e.g., 'EURUSD'). If None, includes all symbols.
                - position_type: Type of position (e.g., mt5.ORDER_TYPE_BUY or mt5.ORDER_TYPE_SELL). If None, includes all positions.

            Returns:
                Tuple[int, pd.DataFrame]: Total opened positions and DataFrame containing information about opened positions.
        """
        try:
            opened_positions = mt5.positions_get()
            df_opened_positions = pd.DataFrame(list(opened_positions), columns=opened_positions[0]._asdict().keys())
            if not symbol and position_type is None:
                df = df_opened_positions
            elif symbol and position_type is None:
                df = df_opened_positions[df_opened_positions["symbol"] == symbol]
            elif not symbol and position_type is not None:
                df = df_opened_positions[df_opened_positions["type"] == position_type]
            else:
                df = df_opened_positions[
                    (df_opened_positions["symbol"] == symbol) & (df_opened_positions["type"] == position_type)
                    ]
            total_opened_positions = len(df)

        except Exception as e:
            # print(e)
            total_opened_positions = 0
            df = pd.DataFrame()

        return total_opened_positions, df

    def get_all_positions(self):
        """
            Get information about all positions.

            Returns:
                pd.DataFrame: DataFrame containing information about all positions.
        """
        try:
            opened_positions = mt5.positions_get()
            df_opened_positions = pd.DataFrame(list(opened_positions), columns=opened_positions[0]._asdict().keys())
        except Exception as e:
            # print(e)
            df_opened_positions = pd.DataFrame()

        return df_opened_positions

    def send_to_break_even(self, df: pd.DataFrame, percentage: float):
        """
            Adjust stop-loss to break-even based on a percentage.

            Args:
                - df (pd.DataFrame): DataFrame containing information about opened positions.
                - percentage (float): Percentage distance from the open price for setting the break-even.
        """
        if not df.empty:
            for symbol in df["symbol"].unique().tolist():
                df_symbol = df[df["symbol"] == symbol]
                if not df_symbol.empty:
                    ticket = df_symbol["ticket"].iloc[0]
                    open_price = df_symbol["price_open"].iloc[0]
                    current_tp = df_symbol["tp"].iloc[0]
                    type_position = df_symbol["type"].iloc[0]
                    current_price = df_symbol["price_current"].iloc[0]

                    # 1 Sell / 0 Buy
                    if type_position == 1:
                        # action = mt5.ORDER_TYPE_BUY
                        distance = open_price - current_price
                        limit_price = open_price - percentage * distance

                        if current_price <= limit_price:
                            modify_order_request = {
                                "action": mt5.TRADE_ACTION_SLTP,
                                "symbol": symbol,
                                "position": ticket.item(),
                                "type": mt5.ORDER_TYPE_BUY,
                                "sl": open_price.item(),
                                "tp": current_tp,
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC,
                            }
                            mt5.order_send(modify_order_request)
                    if type_position == 0:
                        distance = current_tp - open_price
                        limit_price = open_price + percentage * distance

                        if current_price >= limit_price:
                            modify_order_request = {
                                "action": mt5.TRADE_ACTION_SLTP,
                                "symbol": symbol,
                                "position": ticket.item(),
                                "type": mt5.ORDER_TYPE_SELL,
                                "sl": open_price.item(),
                                "tp": current_tp,
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC,
                            }
                            mt5.order_send(modify_order_request)

    def calculate_position_size(self, symbol: str, stop_loss: float, per_to_risk: float):
        """
            Calculate position size based on risk parameters.

            Args:
                - symbol (str): Trading symbol (e.g., 'EURUSD').
                - stop-loss (float): Stop-loss value.
                - per_to_risk (float): Percentage of risk per trade.

            Returns:
                float: Calculated position size.
        """
        mt5.symbol_select(symbol, True)
        symbol_info_tick = mt5.symbol_info_tick(symbol)
        symbol_info = mt5.symbol_info(symbol)

        current_price = (symbol_info_tick.bid + symbol_info_tick.ask) / 2
        tick_size = symbol_info.trade_tick_size

        balance = mt5.account_info().balance
        risk_per_trade = per_to_risk
        ticks_at_risk = abs(current_price - stop_loss) / tick_size
        tick_value = symbol_info.trade_tick_value

        position_size = round(
            (balance * risk_per_trade) / (ticks_at_risk * tick_value), 2
        )

        return position_size


class CrossOverStrategy(TradingStrategy):
    """
    CrossOverStrategy class implements a simple crossover trading strategy based on moving averages.

    Args:
        - trading_data (TradingData): The trading data source for strategy analysis.

    Attributes:
        - data (TradingData): The trading data source for strategy analysis.

    Methods:
        - signal(): Generates a trading signal based on the crossover strategy.

    Example usage:
    ```python
    # Create an instance of CrossOverStrategy with trading data
    strategy = CrossOverStrategy(trading_data)

    # Get the trading signal
    symbol, signal = strategy.signal()
    ```
    """

    def __init__(self, trading_data: TradingData) -> None:
        """
        Initializes the CrossOverStrategy instance.

        Args:
            - trading_data (TradingData): The trading data source for strategy analysis.
        """
        self.data = trading_data

    def signal(self):
        """
        Generates a trading signal based on the crossover strategy.

        Returns:
            Tuple[str, str]: A tuple containing the trading symbol and the trading signal ('buy', 'sell', or 'hold').
        """
        df = self.data.get_data()
        # Calculate moving averages
        df["MA20"] = df["close"].rolling(window=20).mean()
        df["MA50"] = df["close"].rolling(window=50).mean()

        # Calculate MACD
        df["macd"], df["signal"], _ = talib.MACD(df["close"])
        # Buy condition
        buy_condition = (df["MA20"] > df["MA50"])

        # Sell condition
        sell_condition = (df["MA20"] < df["MA50"])

        # Initialize positions
        df["Position"] = None

        # Set positions based on conditions
        df.loc[buy_condition, "Position"] = "buy"
        df.loc[sell_condition, "Position"] = "sell"

        return self.data.get_symbol(), df["Position"].iloc[-1]


class MT5Data(TradingData):
    """
    MT5Data class for retrieving historical trading data from MetaTrader 5.

    Parameters:
        - login (str): MT5 login.
        - server (str): MT5 server.
        - password (str): MT5 password.
        - terminal_path (str): Path to the MT5 terminal.
        - symbol (str): Trading symbol (e.g., 'EURUSD').
        - time_frame (int): Timeframe for historical data.

    Methods:
        - get_data(): Retrieve historical trading data as a Pandas DataFrame.
        - get_symbol(): Get the trading symbol associated with the data.

    Example usage:
    ```
    mt5_data = MT5Data(login='your_login', server='your_server', password='your_password',
                       terminal_path='path/to/terminal', symbol='EURUSD', time_frame=mt5.TIMEFRAME_H1)
    data_frame = mt5_data.get_data()
    symbol = mt5_data.get_symbol()
    ```
    """

    def __init__(self, login: str, server: str, password: str, terminal_path: str, symbol: str,
                 time_frame: int) -> None:
        """
        Initialize the MT5Data instance.

        Args:
            - login (str): MT5 login.
            - server (str): MT5 server.
            - password (str): MT5 password.
            - terminal_path (str): Path to the MT5 terminal.
            - symbol (str): Trading symbol (e.g., 'EURUSD').
            - time_frame (int): Timeframe for historical data.
        """
        mt5.initialize()
        mt5.login(login=login, server=server, password=password, path=terminal_path)
        self.symbol = symbol
        self.time_frame = time_frame

    def get_data(self) -> pd.DataFrame:
        """
        Retrieve historical trading data as a Pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing historical trading data.
        """
        rates = mt5.copy_rates_from_pos(self.symbol, self.time_frame, 0, 1000)
        rates_frame = pd.DataFrame(rates)
        rates_frame["time"] = pd.to_datetime(rates_frame["time"], unit="s")
        return rates_frame

    def get_symbol(self) -> str:
        """
        Get the trading symbol associated with the data.

        Returns:
            str: Trading symbol.
        """
        return self.symbol
