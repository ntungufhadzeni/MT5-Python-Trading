import os
import time
from dotenv import load_dotenv
import MetaTrader5 as mt5
import sched
import threading
from loguru import logger

from mt5_trading.domain import MT5Data, CrossOverStrategy, MT5Trader
from mt5_trading.robot.cross_over_robot import CrossOverRobot
from mt5_trading.logging_config import configure_logging

load_dotenv()
configure_logging()  # added

terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")
server = os.getenv("SERVER")
symbol = "EURUSD"
lot_size = 0.1
print("password", password)
eurusd_h1_data = MT5Data(login, server, password, terminal_path, symbol, mt5.TIMEFRAME_H1)
cross_over_strategy = CrossOverStrategy(eurusd_h1_data)
mt5_trader = MT5Trader()
cross_over_robot = CrossOverRobot(lot_size, mt5_trader, cross_over_strategy)

# Scheduler setup: run every 60 minutes
scheduler = sched.scheduler(time.time, time.sleep)


def run_job():
    try:
        logger.info("Running scheduled trade cycle...")
        cross_over_robot.trade()
        logger.info("Trade cycle completed.")
    except Exception as e:
        logger.exception(f"Scheduled job failed: {e}")


def schedule_hourly():
    run_job()
    scheduler.enter(60 * 60, 1, schedule_hourly)


def start_scheduler():
    scheduler.enter(0, 1, schedule_hourly)
    t = threading.Thread(target=scheduler.run, daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    logger.info("Starting scheduler (every 60 minutes)...")
    start_scheduler()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
