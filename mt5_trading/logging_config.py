import sys
from loguru import logger


def configure_logging(log_path: str = "log.txt") -> None:
    logger.remove()

    logger.add(sys.stdout, level="INFO", enqueue=True, backtrace=True, diagnose=False)

    logger.add(
        log_path,
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )
