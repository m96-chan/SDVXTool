from abc import ABC, abstractmethod

from packages.sdvx.difficulty_table import SDVXDifficultyTable, SDVXDifficultyClass, SDVXNoteType
from packages.sdvx.music import SDVXNote


class SDVXDifficultyTableLoader(ABC):
    @abstractmethod
    def level(self) -> int:
        raise NotImplemented("let's impl!!")

    @abstractmethod
    def parse_classes(self) -> list[SDVXDifficultyClass]:
        raise NotImplemented("let's impl!!")

    def load(self) -> SDVXDifficultyTable:
        return SDVXDifficultyTable(self.level(), self.parse_classes())
