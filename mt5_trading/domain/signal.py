from enum import Enum


class Signal(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    NONE = "none"