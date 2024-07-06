from abc import ABC, abstractmethod

class Platform(ABC):

    connected: bool

    @abstractmethod
    def connect() -> None:
        pass
    
    @abstractmethod
    def gather_scans() -> list:
        pass

    