import csv
import os
from itertools import groupby

from packages.sdvx.music_loader.loader import SDVXMusicLoader
from packages.sdvx.music import SDVXMusic, SDVXNote


class CSVFileSDVXMusicLoader(SDVXMusicLoader):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def load(self) -> list[SDVXMusic]:
        if not os.path.exists(self._file_path):
            return []
        with open(self._file_path, 'r') as f:
            _ = f.readline()  # Headerなんで読み飛ばす
            csv_reader = csv.reader(f)
            rows = [r for r in csv_reader]
        # hashでグループ化する
        return [self._to_music(g) for _, g in groupby(rows, key=lambda x: x[0])]

    @staticmethod
    def _to_music(group):
        difficulties = []
        records = list(group)
        [_, genres, name, author, _, _, _, _, _] = records[0]
        for r in records:
            [_, _, _, _, diff_name, level, image, illustrated, effected] = r
            difficulties.append(SDVXNote(name, diff_name, level, image, illustrated, effected))

        return SDVXMusic(genres.split(','), name, author, difficulties)
