from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.scrollview import MDScrollView
from easyword.database.manager import db_manager

class LibraryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        self.layout = MDBoxLayout(orientation='vertical')
        
        self.layout.add_widget(MDLabel(
            text="我的词库", 
            halign="center", 
            theme_text_color="Primary", 
            font_style="H5",
            size_hint_y=None, 
            height=50
        ))
        
        self.scroll = MDScrollView()
        self.list_container = MDList()
        self.scroll.add_widget(self.list_container)
        
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def refresh(self):
        self.list_container.clear_widgets()
        words = db_manager.get_words_by_library(1)
        if not words:
            self.list_container.add_widget(OneLineListItem(text="词库为空"))
        else:
            for word in words:
                self.list_container.add_widget(OneLineListItem(text=word['word']))
