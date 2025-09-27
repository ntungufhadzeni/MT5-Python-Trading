from abc import ABC, abstractmethod

class TradingData(ABC):
    @abstractmethod
    def get_data(self):
        raise NotImplemented

    @abstractmethod
    def get_symbol(self):
        raise NotImplemented