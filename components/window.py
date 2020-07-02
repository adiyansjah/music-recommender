import os
import time
import threading

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.uix.textinput import TextInput
from components import sidebar
from components import audio_control
from components.track_list import TrackListRecycleView, \
    SpotifyRecycleView, SearchInputSpotify, SearchInputText

from libs import recommender
from utils import config, manager
from utils.manager import DataManager, music_local, is_connected


class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.content = ContentInterface()
        self.add_widget(self.content)


class LoadingScreen(AnchorLayout):
    message = StringProperty()


class ErrorScreen(AnchorLayout):
    icon = StringProperty()
    message = StringProperty()


class AboutScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(AboutScreen, self).__init__(**kwargs)


class SettingScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(SettingScreen, self).__init__(**kwargs)


class ContentInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(ContentInterface, self).__init__(**kwargs)


class HeaderTitle(Label):
    def __init__(self, title, **kwargs):
        super(HeaderTitle, self).__init__(**kwargs)
        self.text = title


class Content(BoxLayout):
    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.app.content = self
        self.loading = LoadingScreen()
        self.error = ErrorScreen()

    @mainthread
    def show_loading(self, message='Loading ...'):
        if self.loading not in self.children:
            self.loading.message = message
            self.add_widget(self.loading)

    @mainthread
    def hide_loading(self):
        if self.loading in self.children:
            self.remove_widget(self.loading)

    def show_no_music(self):
        self.error.icon = 'assets/icons/empty-box.png'
        self.error.message = 'Music is not found'
        self.add_widget(self.error)

    def show_no_connection(self):
        self.error.icon = 'assets/icons/cloud-off.png'
        self.error.message = 'No internet connection'
        self.add_widget(self.error)

    def load_local_music(self, method=1):
        title = 'Local Music #{}'.format(method)
        self.app.method = method
        self.clear_widgets()
        self.show_loading('Loading music ...')
        threading.Thread(target=self.async_load_music, args=(title,)).start()

    def load_spotify_music(self, method=1, keyword='genre:jazz'):
        title = 'Spotify Music #{}'.format(method)
        self.app.method = method
        self.clear_widgets()
        self.show_loading('Fetching music ...')
        threading.Thread(target=self.async_load_spotify,
                         args=(title, method, keyword)).start()

    @mainthread
    def load_setting(self):
        self.clear_widgets()
        self.add_widget(HeaderTitle('Setting'))
        self.add_widget(SettingScreen())

    def load_about(self):
        self.clear_widgets()
        self.add_widget(HeaderTitle('About'))
        self.add_widget(AboutScreen())

    def load_recommendation(self, audio):
        title = 'Recommendation'
        self.clear_widgets()
        self.show_loading('Collecting Recommendations ...')
        threading.Thread(target=self.async_load_recommendation,
                         args=(title, audio)).start()

    def async_load_recommendation(self, header, audio):
        filter_genre = self.app.method == 2
        data = recommender.get_recommend(audio, filter_genre)
        App.get_running_app().sound.data = data
        self.hide_loading()
        self.add_widget(HeaderTitle(header))
        self.add_widget(TrackListRecycleView(data))

    def async_load_music(self, header):
        data = DataManager().load_local_music()
        App.get_running_app().sound.data = data

        self.rv = TrackListRecycleView(data)
        self.header = HeaderTitle(header)
        self.hide_loading()
        self.add_widget(self.header)

        Clock.schedule_once(lambda d: self.add_widget(
            SearchInputText(self.rv)), -1)
        Clock.schedule_once(lambda d: self.add_widget(self.rv), -1)

    def async_load_spotify(self, header, method, keyword):
        manager = DataManager()
        data = manager.load_spotify_music(keyword)

        self.rv = SpotifyRecycleView(data)
        self.header = HeaderTitle(header)

        if not is_connected:
            self.hide_loading()
            Clock.schedule_once(lambda d: self.show_no_connection(), 0)
            return

        try:
            self.rv.data = [next(data)]
        except StopIteration:
            self.hide_loading()
            self.add_widget(self.header)
            Clock.schedule_once(lambda d: self.add_widget(
                SearchInputSpotify(self, method)), 0)
            Clock.schedule_once(lambda d: self.show_no_music(), 0)
            return

        self.hide_loading()
        self.add_widget(self.header)

        Clock.schedule_once(lambda d: self.add_widget(
            SearchInputSpotify(self, method)), 0)
        Clock.schedule_once(lambda d: self.add_widget(self.rv), 0)

    def update_loading_message(self, filename):
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                self.loading.message = f.readline()


class ClearTemp(Button):
    def on_press(self):
        for item in os.listdir(config.temp_directory):
            item = os.path.join(config.temp_directory, item)
            if not os.path.isdir(item):
                os.remove(item)
        popup = Popup(title='Message',
              content=Label(text='Successfully clear temporary folder.'),
              size_hint=(None, None), size=(300,100))
        popup.open()
        Clock.schedule_once(lambda d: popup.dismiss(), 1)


class GenerateData(Button):
    def on_press(self):
        app = App.get_running_app()
        progress = os.path.join(config.temp_abs, "progress.txt")
        app.content.clear_widgets()
        app.content.show_loading()
        event = Clock.schedule_interval(
            lambda t: app.content.update_loading_message(progress), 0.1)
        threading.Thread(
            target=recommender.generate_data,args=(event,app)).start()


class AudioLocation(TextInput):
    def __init__(self, **kwargs):
        super(AudioLocation, self).__init__(**kwargs)
        self.text = config.local_directory


class SetLocation(Button):
    def on_press(self):
        loc = self.location.text
        if (os.path.isdir(loc)):
            manager.scaned_folder = False
            config.update(loc)
            popup = Popup(title='Message',
                content=Label(text='Successfully set new location.'),
                size_hint=(None, None), size=(300,100))
            popup.open()
            Clock.schedule_once(lambda d: popup.dismiss(), 1)
        else:
            popup = Popup(title='Message',
                content=Label(text='Failed to set location.'),
                size_hint=(None, None), size=(300,100))
            popup.open()
            Clock.schedule_once(lambda d: popup.dismiss(), 1)