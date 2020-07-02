from kivy import utils
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from utils.manager import music_local, DataManager


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    ''' Add selection and focus behavior to the view. '''


class TrackListRecycleView(RecycleView):
    def __init__(self, data, **kwargs):
        super(TrackListRecycleView, self).__init__(**kwargs)
        self.data = data


class TrackListItem(RecycleDataViewBehavior, BoxLayout):
    index = NumericProperty()
    order = NumericProperty()
    title = StringProperty()
    artist = StringProperty()
    source = StringProperty()
    duration = NumericProperty()
    is_selected = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(TrackListItem, self).refresh_view_attrs(
            rv, index, data)

    def apply_selection(self, rv, index, is_selected):
        self.is_selected = is_selected

    def on_touch_down(self, touch):
        if super(TrackListItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.app.sound.index = -1
                self.app.sound.index = self.order
            return self.parent.select_with_touch(
                self.index, touch)


class SpotifyRecycleView(RecycleView):
    def __init__(self, iterator, **kwargs):
        super(SpotifyRecycleView, self).__init__(**kwargs)
        self.iterator = iterator
        self.data = []
        self.on = True


class SpotifyItem(TrackListItem):
    id = StringProperty()
    url = StringProperty()

    def refresh_view_attrs(self, rv, index, data):
        should_fetch = (len(rv.data) - index) <= 30
        if should_fetch and rv.on:
            try:
                rv.data.append(next(rv.iterator))
                self.app.sound.data = rv.data
            except StopIteration:
                pass
        self.index = index
        return super(SpotifyItem, self).refresh_view_attrs(
            rv, index, data)


class SearchInputText(TextInput):
    def __init__(self, rv, **kwargs):
        super(SearchInputText, self).__init__(**kwargs)
        self.bind(on_text_validate=self.on_enter)
        self.rv = rv

    def on_enter(self, instance):
        manager = DataManager()
        if 'genre:' in instance.text.lower()[:6]:
            genre = instance.text.lower()[6:]
            self.rv.data = manager.load_local_genre(genre)
            self.app.sound.data = self.rv.data
        else:
            title = instance.text.lower()
            self.rv.data = manager.load_local_title(title)
            self.app.sound.data = self.rv.data


class SearchInputSpotify(TextInput):
    def __init__(self, window, method, **kwargs):
        super(SearchInputSpotify, self).__init__(**kwargs)
        self.bind(on_text_validate=self.on_enter)
        self.window = window
        self.method = method

    def on_enter(self, instance):
        if len(instance.text.strip()) == 0:
            return
        self.window.load_spotify_music(
            self.method, instance.text)


class TrackDropDown(DropDown):
    auto_width = False
    track = None


class TrackMenuButton(Image):
    ICON_SRC_BUTTON = 'assets/icons/option-button.png'

    def __init__(self, **kwargs):
        super(TrackMenuButton, self).__init__(**kwargs)
        self.dropdown = TrackDropDown()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dropdown.track = self.track
            return self.dropdown.open(self)


class GetRecommendButton(Button):
    def __init__(self, **kwargs):
        super(GetRecommendButton, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.color = utils.rgba('#171717')
            audio = self.app.sound.source
            self.app.content.load_recommendation(audio)
            self.dropdown.dismiss()
            return True
