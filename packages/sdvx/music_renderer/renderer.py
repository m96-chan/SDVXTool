from abc import ABC, abstractmethod

from packages.sdvx.music import SDVXMusic


class SDVXMusicRenderer(ABC):
    @abstractmethod
    def render(self, musics: list[SDVXMusic]) -> None:
        raise NotImplemented("let's impl!!")

