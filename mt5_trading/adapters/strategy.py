from abc import ABC, abstractmethod


class TradingStrategy(ABC):
    @abstractmethod
    def signal(self):
        raise NotImplemented
