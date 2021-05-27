from abc import ABC, abstractmethod

from packages.sdvx.music import SDVXMusic


class SDVXMusicLoader(ABC):
    @abstractmethod
    def load(self) -> list[SDVXMusic]:
        raise NotImplemented("let's impl!!")


