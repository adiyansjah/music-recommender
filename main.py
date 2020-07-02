from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from utils.manager import SoundManager
from components.window import MainWindow


class MusicApp(App):
    def __init__(self, **kwargs):
        super(MusicApp, self).__init__(**kwargs)
        #self.sound = SoundManager()

    def build(self):
        return MainWindow()


if __name__ == '__main__':
    MusicApp().run()
