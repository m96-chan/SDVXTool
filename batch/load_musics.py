"""
本家のページから、曲データをロードしてくるバッチ
スリープタイムを設定するとよしなに、間を開けてくれるので、そこそこあけよう（サーバー落とすダメ絶対
"""
import csv
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://p.eagate.573.jp/game/sdvx/vi/music/index.html"
BASE_PARSED = urlparse(BASE_URL)
DETAIL_URL = "https://p.eagate.573.jp/game/sdvx/vi/music/detail.html"
SLEEP_TIME = 500


@dataclass
class SDVXMusic:
    # 楽曲データ
    music_id: str
    genres: list[str]
    name: str
    author: str
    nov: int
    adv: int
    exh: int
    ext_name: Optional[str] = None
    ext_rank: Optional[int] = None

    @property
    def detail_url(self):
        return DETAIL_URL + '?music_id=' + self.music_id

    def image_name(self, difficulty: str):
        return f"{self.music_id}_{difficulty}.jpg"

    def image_names(self) -> list[str]:
        if not self.ext_name:
            return [self.image_name('nov'), self.image_name('adv'), self.image_name('exh')]
        return [self.image_name('nov'), self.image_name('adv'), self.image_name('exh'), self.image_name(self.ext_name)]


def parse_music(music: Tag) -> Optional[SDVXMusic]:
    genre_tags = music.find_all('div', {"class": "genre"})
    if not genre_tags:
        return None
    genres = [g.text for g in genre_tags]
    info_tag = music.find('div', {"class": "info"})
    if not info_tag:
        return None
    [name, author] = [p.text for p in info_tag.find_all('p')]
    nov = int(music.find('p', {'class': "nov"}).text)
    adv = int(music.find('p', {'class': "adv"}).text)
    exh = int(music.find('p', {'class': "exh"}).text)

    ext_rank_tag = music.find('p', {'class': "mxm"}) or \
                   music.find('p', {'class': "vvd"}) or \
                   music.find('p', {'class': "hvn"}) or \
                   music.find('p', {'class': "grv"}) or \
                   music.find('p', {'class': "inf"})

    ext_rank_name = ext_rank_tag and ext_rank_tag.attrs['class'][0]
    ext_rank = ext_rank_tag and int(ext_rank_tag.text)

    detail_tag = music.find('a', {"class": "detail_pop"})
    if not detail_tag:
        return None
    detail_path = detail_tag.attrs['href']
    [music_id] = parse_qs(urlparse(detail_path).query)['music_id']

    return SDVXMusic(
        music_id,
        genres,
        name,
        author,
        nov,
        adv,
        exh,
        ext_rank_name,
        ext_rank
    )


def parse_detail(url: str):
    site = requests.get(url)
    soup = BeautifulSoup(site.content, 'html.parser')
    for tag in soup.find_all('div', {"class": "cat"}):
        [diff_name] = tag.find(name='p').attrs['class']
        img_url = f"{BASE_PARSED.scheme}://{BASE_PARSED.hostname}{tag.img.attrs['src']}"
        yield diff_name, img_url


def parse_page(soup: BeautifulSoup) -> list[SDVXMusic]:
    return [parse_music(m) for m in soup.find_all('div', {"class": "music"})]


def download_image(image_url, file_path):
    with open(file_path, mode='wb') as f:
        f.write(requests.get(image_url).content)


def download_images(music: SDVXMusic):
    paths = (f"../images/{n}" for n in music.image_names())
    if all(os.path.exists(p) for p in paths):
        print('skip download...')
        return
    for d, img in parse_detail(music.detail_url):
        path = f"../images/{music.image_name(d)}"
        if os.path.exists(path):
            continue
        time.sleep(SLEEP_TIME / 2000)
        download_image(img, path)


def load_from_csv(path='../dist/musics.csv') -> list[SDVXMusic]:
    if not os.path.exists(path):
        return []
    musics = []
    with open('../dist/musics.csv', "r") as f:
        _ = f.readline()
        reader = csv.reader(f)
        for row in reader:
            print(row)
            [music_id, genres, name, author, nov, adv, exh, ext_name, ext_rank] = row
            musics.append(SDVXMusic(
                music_id, genres.split(','), name, author, int(nov), int(adv), int(exh),
                None if ext_name == "None" else ext_name,
                None if ext_rank == "None" else int(ext_rank)
            ))
    return musics


if __name__ == "__main__":
    site = requests.get(BASE_URL)
    soup = BeautifulSoup(site.content, 'html.parser')
    # 最大ページ数を取得
    select = soup.find('select', {"id": "search_page"})
    if not select:
        print('can not get pages')
        sys.exit(-1)
    max_page = max(int(o.attrs['value']) for o in select.find_all('option'))

    musics = parse_page(soup)
    csv_musics = load_from_csv()

    if not csv_musics or musics[0].music_id != csv_musics[0].music_id:
        exist_id = csv_musics[0].music_id if csv_musics else None
        if index := next((i for i, p in enumerate(musics) if p.music_id == exist_id), None):
            musics = musics[:index] + csv_musics
        else:
            # 全読み込みは遅いから、一旦コメアウト
            for page in range(2, max_page + 1):
                time.sleep(SLEEP_TIME / 1000)
                print(f'reading...page:{page}')
                site = requests.post(BASE_URL, {'page': page})
                soup = BeautifulSoup(site.content, 'html.parser')
                parsed_musics = parse_page(soup)
                if index := next((i for i, p in enumerate(parsed_musics) if p.music_id == exist_id), None):
                    musics += parsed_musics[:index]
                    musics += csv_musics
                    break
                musics += parsed_musics

        with open('../dist/musics.csv', "w+") as f:
            f.writelines("music_id, genres, name, author, nov,adv, exh, ext_name, ext_rank\n")
            for m in musics:
                f.writelines(
                    f"{m.music_id},\"{','.join(m.genres)}\",\"{m.name}\",\"{m.author}\", {m.nov}, {m.adv}, {m.exh}, {m.ext_name}, {m.ext_rank}\n")
    else:
        musics = csv_musics

    for m in musics:
        print(f'download...images:{m.name}')
        download_images(m)
    sys.exit(0)
