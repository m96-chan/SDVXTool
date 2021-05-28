from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from packages.sdvx.music import SDVXNote, SDVXMusic


class SDVXNoteType(Enum):
    NO_TYPE = 0  # 未分類
    BASE_POWER = 1  # 地力
    CHIP = auto()  # 鍵盤
    KNOBS = auto()  # つまみ


@dataclass
class SDVXNoteInfo:
    music: SDVXMusic
    difficulty: str
    note_type: Optional[SDVXNoteType] = None
    trapped: Optional[bool] = None
    individual: Optional[bool] = None
    # 適正難度とか入る予定
    individual_info: Optional[str] = None


@dataclass
class SDVXDifficultyClass:
    name: str
    # ソートの重み　[SS, S, A]とかアルファベット順じゃないこと多いのでもたせる
    tier: int

    # これが本体
    notes: list[SDVXNoteInfo] = None


@dataclass
class SDVXDifficultyTable:
    lv: int
    # 難易度づけされている
    classes: list[SDVXDifficultyClass]
    unregistered: list[SDVXNoteInfo]
