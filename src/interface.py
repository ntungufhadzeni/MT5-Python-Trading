from abc import ABC, abstractmethod


class Trader(ABC):
    @abstractmethod
    def open_position(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def close_positions(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def get_opened_positions(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def get_all_positions(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def send_to_break_even(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def calculate_position_size(self, *args, **kwargs):
        raise NotImplemented


class TradingStrategy(ABC):
    @abstractmethod
    def signal(self):
        raise NotImplemented


class TradingData(ABC):
    @abstractmethod
    def get_data(self):
        raise NotImplemented

    @abstractmethod
    def get_symbol(self):
        raise NotImplemented
