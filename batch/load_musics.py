"""
本家のページから、曲データをロードしてくるバッチ
"""
import sys
import time

from packages.sdvx.music_loader.csv_file import CSVFileSDVXMusicLoader
from packages.sdvx.music_loader.web import WebSDVXMusicLoader
from packages.sdvx.music_renderer.csv_file import CSVFileSDVXMusicRenderer

if __name__ == "__main__":
    lv = 17
    name = None
    out_file = "../dist/17.csv"

    csv_loader = CSVFileSDVXMusicLoader(out_file)
    exists_music = csv_loader.load()

    option = {}
    if exists_music:
        option["stop_hash"] = exists_music[0].hash_id
    if lv:
        option["search_level"] = lv
    if name:
        option["search_level"] = name

    web_loader = WebSDVXMusicLoader(option)
    musics = web_loader.load()
    difficulties = sum([m.find_notes(lambda x: x.lv == lv) for m in musics], [])
    for d in difficulties:
        time.sleep(500 / 1000)
        d.download_image_if_not_exist('../images')
    if musics:
        renderer = CSVFileSDVXMusicRenderer(out_file)
        renderer.render(musics + exists_music)
    sys.exit(0)
