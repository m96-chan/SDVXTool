from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto

from packages.sdvx.music import SDVXNote


class SDVXNoteType(Enum):
    NO_TYPE = 0  # 地力とかわけてない系にも対応
    BASE_POWER = 1  # 地力
    CHIP = auto()  # 鍵盤
    KNOBS = auto()  # つまみ


@dataclass
class SDVXDifficultyClass:
    name: str
    # ソートの重み　[SS, S, A]とかアルファベット順じゃないこと多いのでもたせる
    weight: int

    # これが本体
    notes: defaultdict[SDVXNoteType, list[SDVXNote]] = defaultdict([])


@dataclass
class SDVXDifficultyTable:
    lv: int
    classes: list[SDVXDifficultyClass]
