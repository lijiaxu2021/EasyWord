from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
import os
import sys

# Import logic modules (reusing existing logic)
from .database.manager import db_manager
from .utils.logger import Logger

# Import UI screens
from .ui.study_screen import StudyScreen
from .ui.quiz_screen import QuizScreen
from .ui.library_screen import LibraryScreen
from .ui.search_screen import SearchScreen
from .ui.settings_screen import SettingsScreen

class EasyWordApp(MDApp):
    def build(self):
        self.title = "EasyWord"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.theme_style = "Light"
        
        # Init Data Path
        if platform == 'android':
            from android.storage import app_storage_path
            self.data_dir = os.path.join(app_storage_path(), 'EasyWord')
        else:
            self.data_dir = os.path.join(os.path.expanduser("~"), ".easyword")
            
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Init Logger
        self.logger = Logger(os.path.join(self.data_dir, 'logs'))
        
        # Init DB
        db_path = self.data_dir
        print(f"Initializing DB at: {db_path}")
        db_manager.init_db(db_path)
        self.db_manager = db_manager

        # Root Layout: Bottom Navigation
        # Note: KivyMD 1.2.0 BottomNavigation structure might differ slightly, using standard approach
        return Builder.load_string('''
MDScreen:
    MDBottomNavigation:
        id: nav_bar
        selected_color_background: "blue"
        text_color_active: "lightgrey"

        MDBottomNavigationItem:
            name: 'study'
            text: '学习'
            icon: 'book-open-page-variant'
            on_tab_press: app.on_tab_switch('study')
            
            StudyScreen:
                id: study_screen

        MDBottomNavigationItem:
            name: 'search'
            text: '查词'
            icon: 'magnify'
            on_tab_press: app.on_tab_switch('search')

            SearchScreen:
                id: search_screen

        MDBottomNavigationItem:
            name: 'quiz'
            text: '检验'
            icon: 'clipboard-text-outline'
            on_tab_press: app.on_tab_switch('quiz')

            QuizScreen:
                id: quiz_screen

        MDBottomNavigationItem:
            name: 'library'
            text: '词库'
            icon: 'bookshelf'
            on_tab_press: app.on_tab_switch('library')

            LibraryScreen:
                id: library_screen
''')

    def on_start(self):
        # Initial load if needed
        pass

    def on_tab_switch(self, tab_name):
        # Refresh screens when tab is switched
        screen = self.root.ids.get(f"{tab_name}_screen")
        if screen and hasattr(screen, 'refresh'):
            screen.refresh()
            
    def show_settings(self):
        # Open settings screen (modal or push)
        # For simplicity, maybe just push a screen if we had a ScreenManager root
        # But we have BottomNav. We can open a dialog or a new screen on top.
        pass

if __name__ == '__main__':
    EasyWordApp().run()
