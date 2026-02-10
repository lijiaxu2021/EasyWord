from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.lang import Builder

class StudyScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Placeholder
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(MDLabel(text="今日学习", halign="center", theme_text_color="Primary", font_style="H4"))
        
        btn = MDRaisedButton(text="开始学习", pos_hint={'center_x': 0.5})
        layout.add_widget(btn)
        
        layout.add_widget(MDLabel(text="（Kivy版本开发中...）", halign="center"))
        
        self.add_widget(layout)
        
    def refresh(self):
        print("Refreshing Study Screen")
