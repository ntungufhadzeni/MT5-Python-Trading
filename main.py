import os
import time
from dotenv import load_dotenv
import MetaTrader5 as mt5

from src.classes import MT5Data, CrossOverStrategy, MT5Trader
from src.robot import CrossOverRobot

load_dotenv()

terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"

data = MT5Data(os.getenv("LOGIN"), os.getenv("SERVER"), os.getenv("PASSWORD"), terminal_path, "EURUSD",
               mt5.TIMEFRAME_H1)
cross_over_strategy = CrossOverStrategy(data)
mt5_trader = MT5Trader()
cross_over_robot = CrossOverRobot(0.1, mt5_trader, cross_over_strategy)

while True:
    cross_over_robot.trade()
    time.sleep(60 * 60)
