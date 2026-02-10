from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

class LibraryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MDLabel(text="词库管理 (Kivy)", halign="center"))
    def refresh(self): pass
