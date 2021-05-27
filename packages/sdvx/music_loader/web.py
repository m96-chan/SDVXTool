import time
from copy import deepcopy
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup, Tag

from packages.sdvx.music import SDVXNote, SDVXMusic
from packages.sdvx.music_loader.loader import SDVXMusicLoader


class LazyBeautifulSoup:
    def __init__(self, method, url, **kwargs):
        self._method = method
        self._url = url
        self._kwargs = kwargs
        self._soup = None

    def get_soup(self) -> BeautifulSoup:
        if not self._soup:
            self._request_data()
        return self._soup

    def _request_data(self):
        site = requests.request(self._method, self._url, **self._kwargs)
        self._soup = BeautifulSoup(site.content, 'html.parser')


class WebSDVXMusicLoader(SDVXMusicLoader):
    BASE_URL = "https://p.eagate.573.jp/game/sdvx/vi/music/index.html"
    BASE_PARSED = urlparse(BASE_URL)
    SLEEP_TIME = 500

    def __init__(self, option: dict):
        self._search_name = option.get('search_name')
        self._search_level = option.get('search_level')
        # keyword lv 検索機能優先 のページ決め打ち機能
        self._page = 1 if (self._search_name or self._search_level) else option.get('page', 1)
        # load_stop機能 差分更新とかで使う
        self._load_stop_hash = option.get('stop_hash')

    def _detect_lazy_soup(self) -> list[LazyBeautifulSoup]:
        post_data = {}
        if self._search_name:
            post_data['search_name'] = self._search_name
        if self._search_level:
            post_data['search_level'] = self._search_level
        post_data['page'] = self._page
        first = LazyBeautifulSoup('post', self.BASE_URL, data=post_data)
        soup = first.get_soup()
        max_page = self._parse_max_page(soup)
        lazy_soups = [first]
        for page in range(2, max_page + 1):
            data = deepcopy(post_data)
            data['page'] = page
            lazy_soups.append(
                LazyBeautifulSoup('post', self.BASE_URL, data=data)
            )
        return lazy_soups

    def load(self) -> list[SDVXMusic]:
        musics = []
        for lazy_soup in self._detect_lazy_soup():
            parsed, is_stop = self._parse_musics(lazy_soup.get_soup())
            if is_stop:
                break
            musics += parsed
        return musics

    def _parse_musics(self, soup: BeautifulSoup) -> tuple[list[SDVXMusic], bool]:
        musics = []
        is_stop = False
        for music_tag in soup.select("div.music"):
            time.sleep(self.SLEEP_TIME / 1000)
            music = self._parse_music(music_tag)
            musics.append(music)
            print(f"{music.name} loaded!")
            if is_stop := self._load_stop_hash == music.hash_id:
                break
        return musics, is_stop

    def _parse_music(self, music: Tag) -> SDVXMusic:
        genre_tags = music.find_all('div', {"class": "genre"})
        if not genre_tags:
            raise KeyError('genre tag not found!')
        genres = [g.text for g in genre_tags]
        info_tag = music.find('div', {"class": "info"})
        if not info_tag:
            raise KeyError('info tag not found!')
        [name, author] = [p.text for p in info_tag.find_all('p')]
        detail_tag = music.find('a', {"class": "detail_pop"})
        if not detail_tag:
            raise KeyError('info tag not found!')
        detail_path = detail_tag.attrs['href']
        detail_url = f"{self.BASE_PARSED.scheme}://{self.BASE_PARSED.hostname}{detail_path}"
        diffs = self._load_notes(name, detail_url)
        return SDVXMusic(genres, name, author, diffs)

    def _load_notes(self, music_name, detail_url: str) -> list[SDVXNote]:
        site = requests.get(detail_url)
        soup = BeautifulSoup(site.content, 'html.parser')
        return [self._load_note(music_name, t) for t in soup.select('div.cat')]

    @staticmethod
    def _load_note(music_name:str, cat: Tag) -> SDVXNote:
        [diff, illustrated, effected] = cat.select('p')
        [name] = diff.attrs['class']
        [image] = parse_qs(urlparse(cat.select_one('img').attrs['src']).query)['img']
        return SDVXNote(
            music_name,
            name,
            int(diff.text),
            image,
            illustrated.text,
            effected.text
        )

    @staticmethod
    def _parse_max_page(soup: BeautifulSoup):
        # 最大ページ数を取得
        select = soup.find('select', {"id": "search_page"})
        if not select:
            raise KeyError('page select tag not found!')
        return max(int(o.attrs['value']) for o in select.find_all('option'))
