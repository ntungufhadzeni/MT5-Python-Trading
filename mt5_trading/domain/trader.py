import MetaTrader5 as mt5
import pandas as pd
from loguru import logger

from mt5_trading.adapters import Trader


class MT5Trader(Trader):
    def open_position(self, symbol, volume, position_type, comment, magic_number, sl=None, tp=None):
        # Base order dictionary with common parameters
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

        # Add optional parameters if they are provided
        if sl is not None:
            order["sl"] = sl
        if tp is not None:
            order["tp"] = tp

        result = mt5.order_send(order)

        if result and result.retcode == 10027:  # AutoTrading disabled error code
            logger.error("AutoTrading is disabled in MetaTrader 5")
            logger.error("Please enable AutoTrading: Tools -> Options -> Expert Advisors -> Allow Automated Trading")
            return None

        return result

    def close_positions(self, robot_name: str, symbol=None, position_type=None):
        df_open_positions = self.get_all_positions()

        if not df_open_positions.empty:
            if not symbol and position_type is None:
                position_list = df_open_positions["ticket"].unique().tolist()
            elif symbol and position_type is None:
                df_open_positions = df_open_positions[df_open_positions["symbol"] == symbol]
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
        except Exception:
            total_opened_positions = 0
            df = pd.DataFrame()
        return total_opened_positions, df

    def get_all_positions(self):
        try:
            opened_positions = mt5.positions_get()
            df_opened_positions = pd.DataFrame(list(opened_positions), columns=opened_positions[0]._asdict().keys())
        except Exception:
            df_opened_positions = pd.DataFrame()
        return df_opened_positions

    def send_to_break_even(self, df: pd.DataFrame, percentage: float):
        if not df.empty:
            for symbol in df["symbol"].unique().tolist():
                df_symbol = df[df["symbol"] == symbol]
                if not df_symbol.empty:
                    ticket = df_symbol["ticket"].iloc[0]
                    open_price = df_symbol["price_open"].iloc[0]
                    current_tp = df_symbol["tp"].iloc[0]
                    type_position = df_symbol["type"].iloc[0]
                    current_price = df_symbol["price_current"].iloc[0]

                    if type_position == 1:
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
        mt5.symbol_select(symbol, True)
        symbol_info_tick = mt5.symbol_info_tick(symbol)
        symbol_info = mt5.symbol_info(symbol)

        current_price = (symbol_info_tick.bid + symbol_info_tick.ask) / 2
        tick_size = symbol_info.trade_tick_size

        balance = mt5.account_info().balance
        risk_per_trade = per_to_risk
        ticks_at_risk = abs(current_price - stop_loss) / tick_size
        tick_value = symbol_info.trade_tick_value

        position_size = round((balance * risk_per_trade) / (ticks_at_risk * tick_value), 2)
        return position_size
