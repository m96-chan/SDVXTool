from packages.sdvx.music import SDVXMusic
from packages.sdvx.music_renderer.renderer import SDVXMusicRenderer


class CSVFileSDVXMusicRenderer(SDVXMusicRenderer):
    """
    正規化せずに、フラットにCSVに詰め込むRenderer
    """
    def __init__(self, file_path: str):
        self._file_path = file_path

    def render(self, musics: list[SDVXMusic]) -> None:
        with open(self._file_path, "w+") as f:
            self._render_head(f)
            for m in musics:
                print(f"{m.name} writing... > {self._file_path}")
                self._render_one(m, f)


    @staticmethod
    def _render_head( f):
        f.writelines("hash,genres,name,author,diff_name,level,image,illustrated,effected\n")

    @staticmethod
    def _render_one(music: SDVXMusic, f):
        for n in music.notes:
            f.writelines(
                f'"{music.hash_id}",'
                f'"{",".join(music.genres)}",'
                f'"{music.name}",'
                f'"{music.author}",'
                f'{n.name},'
                f'{n.lv},'
                f'"{n.image_name}",'
                f'"{n.illustrated_by}",'
                f'"{n.effected_by}"\n'
            )
