from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

class QuizScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MDLabel(text="检验模式 (Kivy)", halign="center"))
    def refresh(self): pass
