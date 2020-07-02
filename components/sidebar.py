from enum import Enum
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, \
    BooleanProperty, ObjectProperty



class Menu(Enum):
    LOCAL_ONE = 1
    LOCAL_TWO = 2
    SPOTIFY_ONE = 3
    SPOTIFY_TWO = 4
    ABOUT = 5
    SETTING = 6


class Sidebar(BoxLayout):
    selected_menu = ObjectProperty()
    first_load = BooleanProperty(False)

    def select_menu(self, value):
        if value == Menu.LOCAL_ONE:
            self.content.load_local_music(method=1)
        elif value == Menu.LOCAL_TWO:
            self.content.load_local_music(method=2)
        elif value == Menu.SPOTIFY_ONE:
            self.content.load_spotify_music(method=1)
        elif value == Menu.SPOTIFY_TWO:
            self.content.load_spotify_music(method=2)
        elif value == Menu.ABOUT:
            self.content.load_about()
        elif value == Menu.SETTING:
            self.content.load_setting()

    def on_first_load(self, ins, val):
        self.content.load_about()


class MenuItem(BoxLayout):
    name = StringProperty()
    is_selected = BooleanProperty(False)
    icon_source = StringProperty()
    icon_source_active = StringProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.selected_menu = self.menu_id
            self.parent.select_menu(self.menu_id)