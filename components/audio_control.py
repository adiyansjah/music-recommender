from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, StringProperty, \
    NumericProperty, ObjectProperty
from utils.manager import AudioState


class PlayButton(Image):
    ICON_SRC_PLAY = 'assets/icons/play-button.png'
    ICON_SRC_PAUSE = 'assets/icons/pause-button.png'
    ICON_SRC_DISABLED_PLAY = 'assets/icons/disabled-play-button.png'

    state = ObjectProperty()

    def on_state(self, instance, value):
        if value == AudioState.PLAY:
            self.source = self.ICON_SRC_PAUSE
        elif value == AudioState.PAUSE:
            self.source = self.ICON_SRC_PLAY
        elif value == AudioState.STOP:
            self.source = self.ICON_SRC_DISABLED_PLAY

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.state == AudioState.PLAY:
                self.sound.pause()
            elif self.state == AudioState.PAUSE:
                self.sound.resume()


class NextButton(Image):
    ICON_SRC_ACTIVE = 'assets/icons/next-button.png'
    ICON_SRC_DISABLED = 'assets/icons/disabled-next-button.png'

    is_active = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.source = self.ICON_SRC_DISABLED
            self.sound.go_next()

    def on_touch_up(self, touch):
        if self.is_active:
            self.source = self.ICON_SRC_ACTIVE


class PreviousButton(Image):
    ICON_SRC_ACTIVE = 'assets/icons/previous-button.png'
    ICON_SRC_DISABLED = 'assets/icons/disabled-previous-button.png'

    is_active = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.source = self.ICON_SRC_DISABLED
            self.sound.go_prev()

    def on_touch_up(self, touch):
        if self.is_active:
            self.source = self.ICON_SRC_ACTIVE


class AudioSlider(Slider):
    disabled = True

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            position = int(self.sound.duration * self.value / self.max)
            self.sound.seek_to(position)


class AudioController(BoxLayout):
    is_active = BooleanProperty()