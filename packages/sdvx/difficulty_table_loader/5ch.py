from packages.sdvx.difficulty_table import SDVXDifficultyTable, SDVXNoteType, SDVXDifficultyClass
from packages.sdvx.difficulty_table_loader.loader import SDVXDifficultyTableLoader


class SDVX5chLv17DifficultyTableLoader(SDVXDifficultyTableLoader):
    def level(self) -> int:
        return 17

    def parse_classes(self) -> list[SDVXDifficultyClass]:
        pass
