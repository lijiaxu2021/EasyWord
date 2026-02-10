from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MDLabel(text="设置与日志 (Kivy)", halign="center"))
