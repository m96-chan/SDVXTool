from abc import ABC, abstractmethod

from packages.sdvx.difficulty_table import SDVXDifficultyTable


class SDVXDifficultyTableRenderer(ABC):
    @abstractmethod
    def render(self, table:SDVXDifficultyTable) -> None:
        raise NotImplemented("let's impl!!")