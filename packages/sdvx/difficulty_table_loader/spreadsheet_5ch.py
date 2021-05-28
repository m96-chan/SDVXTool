import difflib
import re
from abc import ABC
from typing import Optional

from packages.advanced_gspread.models import AdvancedReadOnlyWorkSheet, RGB, AdvancedReadOnlyCell
from packages.sdvx.difficulty_table import SDVXNoteType, SDVXDifficultyClass, SDVXNoteInfo
from packages.sdvx.difficulty_table_loader.loader import SDVXDifficultyTableLoader
from packages.sdvx.music import SDVXMusic


class SDVX5chDifficultyTableLoader(SDVXDifficultyTableLoader, ABC):
    trapped_regex = re.compile(r"【(.*)】(.*)")
    difficulty_regex = re.compile(r".*\[(.{3})].*")
    individual_info_regex = re.compile(r".*\((.*～.*)\)")

    def __init__(self, musics: list[SDVXMusic]):
        self._musics = musics
        # check済みの組み合わせを保存
        self._checked = []

    def detect_music(self, search_name:str) -> Optional[SDVXMusic]:
        # 完全検索優先
        if music := next((m for m in self._musics if search_name == m.name), None):
            return music
        # あいまい検索
        if music := next((m for m in self._musics if search_name in m.name), None):
            print(f"[Warn] is that same? {search_name} = {music.name}")
            return music
        # ゲシュタルトパターンマッチで探しあてる。
        matcher_iter = ((
            difflib.SequenceMatcher(None, search_name, m.name).ratio(), m
        ) for m in self._musics)
        matching = [(r, music) for r, music in matcher_iter if r > 0.5]
        matching.sort(key=lambda x: x[0], reverse=True)
        if not matching:
            print(f"[Alert]{search_name} not found!")
            return None
        (_, music) = matching[0]
        print(f"[Warn] is that same? {search_name} = {music.name}")
        return music


    def parse_music_cell(self, c: AdvancedReadOnlyCell) -> Optional[SDVXNoteInfo]:
        """
        セルから、曲の情報をパースする
        """
        # 背景白は曲ではないと判断（これでいいのか？）
        if c.background_color == RGB({"red": 1, "green": 1, "blue": 1}):
            return None
        # 譜面のタイプ判断
        note_type = SDVXNoteType.NO_TYPE
        if c.background_color == RGB({"red": 1, "green": 0.8980392, "blue": 0.6}):
            note_type = SDVXNoteType.BASE_POWER
        if c.background_color == RGB({"red": 0.8156863, "green": 0.8784314, "blue": 0.8901961}):
            note_type = SDVXNoteType.CHIP
        if c.background_color == RGB({"red": 0.95686275, "green": 0.8, "blue": 0.8}):
            note_type = SDVXNoteType.KNOBS

        # 曲名のパース
        is_trapped = False
        base_name = c.value
        if match := SDVX5chDifficultyTableLoader.trapped_regex.fullmatch(base_name):
            is_trapped = True
            base_name = match.group(1) + match.group(2)

        # 難易度・指定があれば
        difficulty = None
        if match := SDVX5chDifficultyTableLoader.difficulty_regex.fullmatch(base_name):
            u = match.group(1)
            difficulty = u.lower()
            base_name = base_name.replace(f"[{u}]", "")

        # 個人差
        is_individual = base_name.startswith("※")
        if is_individual:
            base_name = base_name.replace("※", "")

        # 詐称難易度
        individual_info = None
        if match := SDVX5chDifficultyTableLoader.individual_info_regex.fullmatch(base_name):
            individual_info = match.group(1)
            base_name = base_name.replace(f"({individual_info})", "")

        music = self.detect_music(base_name)
        if not music:
            return None
        if not difficulty:
            [note] = music.find_notes(lambda x: x.lv == self.level())
            difficulty = note.name

        checked = getattr(music, "check", [])
        checked.append(difficulty)
        setattr(music, "check", checked)
        return SDVXNoteInfo(music, difficulty, note_type, is_trapped, is_individual, individual_info)

    def check_unregistered(self) -> list[SDVXNoteInfo]:
        unregistered_music = (m for m in self._musics if not hasattr(m, "check"))
        unregistered_note_info = [SDVXNoteInfo(m, n.name) for m in unregistered_music for n in m.notes if n.lv == self.level()]
        return unregistered_note_info


class SDVX5chLv17DifficultyTableLoader(SDVX5chDifficultyTableLoader):

    def __init__(self, worksheet: AdvancedReadOnlyWorkSheet, musics: list[SDVXMusic]):
        self._worksheet = worksheet
        super().__init__(musics)

    def level(self) -> int:
        return 17

    def parse_classes(self) -> list[SDVXDifficultyClass]:
        classes: [SDVXDifficultyClass] = []
        # 2列目がクラス定義のヘッダーと決め打ち
        for i, c in enumerate(self._worksheet.row_iter(2)):
            # クラスは、センタリングされているという決め打ち。
            # ルールが変わったら実装変更必要
            if c.horizontal_alignment != 'CENTER':
                continue
            # Tierは左から強いものとする
            classes.append(SDVXDifficultyClass(c.value, i + 1))

        for dc in classes:
            dc.notes = []
            for c in self._worksheet.col_iter(dc.tier):
                # 背景白は曲ではないと判断（これでいいのか？）
                if music := self.parse_music_cell(c):
                    dc.notes.append(music)
        return classes
