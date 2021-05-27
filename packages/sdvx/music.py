import hashlib
import os
from dataclasses import dataclass
from functools import cached_property
from typing import Callable

import requests


@dataclass
class SDVXNote:
    music_name: str
    name: str
    lv: int
    image_name: str
    illustrated_by: str
    effected_by: str

    @cached_property
    def hash_id(self) -> str:
        return hashlib.md5(f"{self.music_name}_{self.name}".encode('utf-8')).hexdigest()

    @cached_property
    def image_url(self):
        return f"https://p.eagate.573.jp/game/sdvx/vi/common/jacket.html?img={self.image_name}"

    def download_image_if_not_exist(self, folder_path: str):
        file_path = os.path.join(folder_path, f"{self.image_name}.jpg")
        # あるから落とさん
        if os.path.exists(file_path):
            return
        with open(file_path, mode='wb') as f:
            print(f"downloading...{self.image_name}")
            f.write(requests.get(self.image_url).content)

    def __eq__(self, other):
        if isinstance(other, SDVXNote):
            return other.hash_id == self.hash_id
        return False

@dataclass
class SDVXMusic:
    genres: list[str]
    name: str
    author: str
    notes: list[SDVXNote]

    @cached_property
    def hash_id(self) -> str:
        return hashlib.md5(f"{self.name}_{self.author}".encode('utf-8')).hexdigest()

    def find_notes(self, filter_func: Callable[[SDVXNote], bool]):
        return [d for d in self.notes if filter_func(d)]