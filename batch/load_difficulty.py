"""
難易度表をいい感じにデータにする
https://docs.google.com/spreadsheets/d/1cFltguBvPplBem-x1STHnG3k4TZzFfyNEZ-RwsQszoo/htmlview#
統一データとして吐き出す予定
"""
import sys

import gspread
from gspread import Spreadsheet

from packages.advanced_gspread.models import AdvancedSpreadsheetReader
from packages.sdvx.difficulty_table_loader.spreadsheet_5ch import SDVX5chLv17DifficultyTableLoader
from packages.sdvx.difficulty_table_renderer.json_file import JsonFileSDVXDifficultyTableRenderer
from packages.sdvx.music_loader.csv_file import CSVFileSDVXMusicLoader

DIFFICULTY_URL = "https://docs.google.com/spreadsheets/d/1cFltguBvPplBem-x1STHnG3k4TZzFfyNEZ-RwsQszoo/htmlview#"


if __name__ == "__main__":
    csv_loader = CSVFileSDVXMusicLoader("../dist/17.csv")
    musics = csv_loader.load()
    if not musics:
        print("first run load_musics...")
        sys.exit(-1)

    gc = gspread.service_account(filename='../keys/sdvxtool.json')
    sh = AdvancedSpreadsheetReader(gc.open_by_url(DIFFICULTY_URL))
    lv17loader = SDVX5chLv17DifficultyTableLoader(sh.worksheet('Lv17'), musics)
    lv17_difficulty_tbl = lv17loader.load()
    JsonFileSDVXDifficultyTableRenderer("../dist/17.json").render(lv17_difficulty_tbl)
    sys.exit(0)
