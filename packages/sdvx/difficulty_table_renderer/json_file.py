import json

from packages.sdvx.difficulty_table import SDVXDifficultyTable, SDVXDifficultyClass, SDVXNoteInfo
from packages.sdvx.difficulty_table_renderer.renderer import SDVXDifficultyTableRenderer


class JsonFileSDVXDifficultyTableRenderer(SDVXDifficultyTableRenderer):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def _tbl_to_dict(self, table: SDVXDifficultyTable) -> dict:
        return {
            "level": table.lv,
            "classes": [self._cls_to_dict(c) for c in table.classes],
            "unregistered": [self._note_to_dict(n) for n in table.unregistered]
        }

    def _cls_to_dict(self, cls: SDVXDifficultyClass) -> dict:
        return {
            "name": cls.name,
            "tier": cls.tier,
            "notes": [self._note_to_dict(n) for n in cls.notes]
        }

    @staticmethod
    def _note_to_dict(note: SDVXNoteInfo) -> dict:
        target_difficulty = next(n for n in note.music.notes if n.name == note.difficulty)
        json_dict = {
            "name": note.music.name,
            "author": note.music.author,
            "difficulty": target_difficulty.name,
            "level": target_difficulty.lv,
            "image": target_difficulty.image_name,
            "illustrated_by": target_difficulty.illustrated_by,
            "effected_by": target_difficulty.effected_by,
        }
        if note.note_type:
            json_dict["note_type"] = note.note_type.name
        if note.trapped:
            json_dict["trapped"] = note.trapped
        if note.individual:
            json_dict["individual"] = note.individual
        if note.individual_info:
            json_dict["individual_info"] = note.individual_info

        return json_dict

    def render(self, table: SDVXDifficultyTable) -> None:
        with open(self._file_path, "w+") as fp:
            json.dump(self._tbl_to_dict(table), fp)
