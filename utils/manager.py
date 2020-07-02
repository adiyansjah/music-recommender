import os
import math
from glob import glob
from enum import Enum
from mutagen.mp3 import EasyMP3
from collections import namedtuple

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, \
    NumericProperty, StringProperty, BooleanProperty

from utils import config
from libs import recommender
from libs.spotify_api import SpotifyClient


music_local = []
scaned_folder = False

try:
    spotify = SpotifyClient(
        config.client_id, config.client_secret)
    spotify.authenticate()
    is_connected = True
except:
    is_connected = False


class DataManager:
    def __init__(self):
        self.local_dir = config.local_directory
        self.keyword = 'genre:pop'

    def load_local_music(self):
        global scaned_folder

        if not scaned_folder:
            files = glob(os.path.join(
                config.local_directory, '**/*.mp3'),
                recursive=True)

            for index, item in enumerate(files):
                audio = EasyMP3(item)
                music_local.append({
                    'order': index,
                    'title': ', '.join(audio.get('title', [item[:-4]])),
                    'artist': ', '.join(audio.get('artist', ['Unknown'])),
                    'duration': int(audio.info.length),
                    'source': item})

            scaned_folder = True
        return music_local

    def load_spotify_music(self, query):
        if not is_connected:
            return iter([])

        counter = 0
        search = spotify.search_track(query)

        def track_artist(artist):
            return ', '.join(
                [artist['name'] for artist in artist])

        def track_source(name):
            return os.path.join(
                config.temp_directory, '{}.mp3'.format(name))

        def track_data(track, order):
            return {'id': track['id'],
                    'order': order,
                    'title': track['name'],
                    'artist': track_artist(track['artists']),
                    'duration': 30,
                    'source': track_source(track['id']),
                    'url': track['preview_url']}

        for result in search:
            if not 'tracks' in result:
                raise StopIteration
            for track in result['tracks']['items']:
                if track['preview_url'] != None:
                    yield track_data(track, counter)
                    counter += 1

    def load_local_genre(self, genre):
        result = []
        counter = 0

        if recommender.filled:
            for index, item in enumerate(recommender.data):
                if item['genre'][0].lower() == genre:
                    result.append({
                        'order': counter,
                        'title': item['title'],
                        'artist': item['artist'],
                        'duration': item['duration'],
                        'source': item['source'],
                    })
                    counter += 1
            return result
        return result

    def load_local_title(self, title):
        result = []
        counter = 0
        for item in music_local:
            if title in item['title'].lower():
                result.append({
                    'order': counter,
                    'title': item['title'],
                    'artist': item['artist'],
                    'duration': item['duration'],
                    'source': item['source'],
                })
                counter += 1
        return result


class AudioState(Enum):
    PLAY = 1
    STOP = 2
    PAUSE = 3


class SoundManager(EventDispatcher):
    data = ObjectProperty()
    index = NumericProperty(None)
    sound = ObjectProperty(None)
    state = ObjectProperty(AudioState.STOP)
    title = StringProperty()
    artist = StringProperty()
    source = StringProperty()
    duration = NumericProperty()
    position = NumericProperty()
    schedule = ObjectProperty(None)
    has_next = BooleanProperty(False)
    has_prev = BooleanProperty(False)
    volume = NumericProperty(1)

    def on_index(self, ins, val):
        if val < 0:
            return

        self.title = self.data[val]['title']
        self.artist = self.data[val]['artist']
        self.duration = self.data[val]['duration']
        self.source = self.data[val]['source']

        if 'url' in self.data[val]:
            self.download(val)

        self.has_next = val < len(self.data) - 1
        self.has_prev = val > 0
        self.stop()
        self.play()

    def download(self, val):
        spotify.download_audio(
            self.data[val]['url'],
            self.data[val]['id'], config.temp_directory)

    def play(self):
        self.sound = SoundLoader.load(
            self.data[self.index]['source'])
        self.sound.play()
        self.state = AudioState.PLAY
        self.start_schedule()

    def pause(self):
        if self.sound and self.state == AudioState.PLAY:
            self.sound.stop()
            self.state = AudioState.PAUSE
            self.stop_schedule()

    def resume(self):
        if self.sound and self.state == AudioState.PAUSE:
            self.state = AudioState.STOP
            self.seek_to(self.position)

    def stop(self):
        if self.sound and self.state == AudioState.PLAY:
            self.sound.stop()
            self.sound.unload()
            self.state = AudioState.STOP
            self.stop_schedule()

    def seek_to(self, position):
        if self.sound and self.state == AudioState.PLAY:
            self.position = position
            self.sound.seek(position)
        if self.sound and self.state == AudioState.STOP:
            self.position = position
            self.sound.seek(position)
            self.sound.play()
            self.sound.seek(self.position)
            self.state = AudioState.PLAY
            self.start_schedule()

    def go_next(self):
        if self.has_next:
            self.index += 1

    def go_prev(self):
        if self.has_prev:
            self.index -= 1

    def start_schedule(self):
        self.schedule = Clock.schedule_interval(
            self.update_info, 0.5)

    def stop_schedule(self):
        self.schedule.cancel()

    def update_info(self, dt):
        self.position = math.ceil(self.sound.get_pos())
        if self.position >= self.duration:
            self.pause()
            self.position = 0

    def format_time(self, duration):
        minute = int(duration / 60)
        second = duration % 60
        return '{}:{:0>2}'.format(minute, second)
