import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import traceback
import os

class EasyWordApp(toga.App):
    def startup(self):
        # Init Logger
        from .utils.logger import Logger
        self.logger = Logger(os.path.join(self.paths.data, 'logs'))
        
        # Main Window
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        # Load App
        self.load_full_app(None)
        
        self.main_window.show()

    def load_full_app(self, widget):
        print("Loading full app...")
        try:
            # Lazy import
            from .database.manager import db_manager
            from .consts import STYLE_ROOT, STYLE_HEADING, STYLE_SUBTITLE, STYLE_CARD, STYLE_BTN_PRIMARY, STYLE_BTN_SECONDARY, COLOR_PRIMARY, COLOR_SURFACE, COLOR_BACKGROUND
            from .ui.library_view import LibraryView
            from .ui.library_detail_view import LibraryDetailView
            from .ui.edit_word_view import EditWordView
            from .ui.create_library_view import CreateLibraryView
            from .ui.bulk_import_view import BulkImportView
            from .ui.word_card import WordCard
            from .ui.quiz_view import QuizView
            from .ui.settings_view import LogListView, LogDetailView
            
            print("Modules imported.")
            
            # Store references
            self.db_manager = db_manager
            self.STYLE_ROOT = STYLE_ROOT
            self.STYLE_HEADING = STYLE_HEADING
            self.STYLE_SUBTITLE = STYLE_SUBTITLE
            self.STYLE_CARD = STYLE_CARD
            self.STYLE_BTN_PRIMARY = STYLE_BTN_PRIMARY
            self.STYLE_BTN_SECONDARY = STYLE_BTN_SECONDARY
            self.COLOR_PRIMARY = COLOR_PRIMARY
            
            # View Classes
            self.LibraryView = LibraryView
            self.LibraryDetailView = LibraryDetailView
            self.EditWordView = EditWordView
            self.CreateLibraryView = CreateLibraryView
            self.BulkImportView = BulkImportView
            self.WordCard = WordCard
            self.QuizView = QuizView
            self.LogListView = LogListView
            self.LogDetailView = LogDetailView
            
            # Init DB
            print(f"Initializing DB at: {self.paths.data}")
            db_manager.init_db(self.paths.data)
            print("DB Initialized.")
            
            # UI Layout: Main Box
            # Use STYLE_ROOT to ensure flex=1
            self.main_layout = toga.Box(style=STYLE_ROOT)
            
            # Content Area (Flex=1 to take all available space)
            self.content_area = toga.Box(style=Pack(flex=1, direction=COLUMN, background_color=COLOR_BACKGROUND))
            
            # Nav Bar (Modern Style, Fixed Height)
            self.nav_bar = toga.Box(style=Pack(
                direction=ROW, 
                height=56, 
                align_items=CENTER, 
                background_color=COLOR_SURFACE
            ))
            
            # Helper to make nav buttons with "icon" feel
            def make_nav_btn(label, icon, handler):
                return toga.Button(
                    f"{icon} {label}", 
                    on_press=handler, 
                    style=Pack(flex=1, height=56, background_color=COLOR_SURFACE, color=COLOR_PRIMARY)
                )

            self.nav_bar.add(make_nav_btn("学习", "📖", lambda w: self.switch_tab(0)))
            self.nav_bar.add(make_nav_btn("检验", "📝", lambda w: self.switch_tab(1)))
            self.nav_bar.add(make_nav_btn("词库", "📚", lambda w: self.switch_tab(2)))

            self.main_layout.add(self.content_area)
            self.main_layout.add(toga.Divider())
            self.main_layout.add(self.nav_bar)
            
            # REMOVED DEBUG LOG FROM UI TO SAVE SPACE
            # self.main_layout.add(toga.Divider())
            # self.main_layout.add(debug_container)

            # Replace content
            self.main_window.content = self.main_layout
            
            # State
            self.current_library_id = 1 # Default
            self.current_tab_index = 2
            
            # Load Library view by default
            self.switch_tab(2) 
            print("UI Built.")
            
        except Exception as e:
            print(f"LOAD FAILED: {e}")
            traceback.print_exc()
            self.main_window.info_dialog("Load Failed", f"Error: {e}")

    def switch_tab(self, index):
        print(f"Switching to tab {index}")
        self.current_tab_index = index
        self.content_area.clear()
        if index == 0:
            self.content_area.add(self.build_study_tab())
        elif index == 1:
            self.content_area.add(self.build_review_tab())
        elif index == 2:
            # Libraries Tab
            self.library_view = self.LibraryView(self, on_select_library=self.on_library_selected)
            self.content_area.add(self.library_view)

    def on_library_selected(self, lib):
        print(f"Selected library: {lib['name']}")
        self.current_library_id = lib['id']
        self.main_window.title = f"EasyWord - {lib['name']}"
        self.show_library_detail(lib)

    def show_library_detail(self, lib, selection_mode='manage'):
        self.content_area.clear()
        detail_view = self.LibraryDetailView(
            self, 
            library=lib, 
            on_back=lambda w=None: self.switch_tab(2) if selection_mode == 'manage' else self.switch_tab(1),
            mode=selection_mode
        )
        self.content_area.add(detail_view)

    def show_edit_word_view(self, word_data, return_view_instance):
        self.content_area.clear()
        
        def on_save():
            self.main_window.info_dialog("成功", "保存成功")
            self.content_area.clear()
            self.content_area.add(return_view_instance)
            return_view_instance.refresh_list()
            
        def on_cancel(widget=None):
            self.content_area.clear()
            self.content_area.add(return_view_instance)
            
        edit_view = self.EditWordView(self, word_data, on_save, on_cancel)
        self.content_area.add(edit_view)

    def show_create_library_view(self):
        self.content_area.clear()
        view = self.CreateLibraryView(self, on_cancel=lambda w=None: self.switch_tab(2))
        self.content_area.add(view)

    def show_bulk_import_view(self, widget=None, library_id=None, return_view=None):
        target_lib_id = library_id if library_id else self.current_library_id
        
        def on_cancel(w=None):
            if return_view:
                self.content_area.clear()
                self.content_area.add(return_view)
                if hasattr(return_view, 'refresh_list'):
                    return_view.refresh_list()
            else:
                self.switch_tab(0)
                
        self.content_area.clear()
        view = self.BulkImportView(self, target_lib_id, on_cancel=on_cancel)
        self.content_area.add(view)

    def show_log_list(self):
        self.content_area.clear()
        view = self.LogListView(self, on_back=lambda w=None: self.switch_tab(0))
        self.content_area.add(view)

    def show_log_detail(self, filename, content, list_view):
        self.content_area.clear()
        view = self.LogDetailView(self, filename, content, on_back=lambda w=None: self.show_log_list())
        self.content_area.add(view)

    def build_study_tab(self):
        self.study_box = toga.Box(style=self.STYLE_ROOT)
        
        # Header
        header_box = toga.Box(style=Pack(
            direction=ROW, 
            padding=15, 
            align_items=CENTER, 
            background_color=self.COLOR_PRIMARY
        ))
        header_box.add(toga.Label("今日学习", style=Pack(font_size=18, font_weight='bold', color='white')))
        header_box.add(toga.Box(style=Pack(flex=1)))
        
        # Log/Settings Button
        btn_settings = toga.Button(
            "⚙", 
            on_press=lambda w: self.show_log_list(), 
            style=Pack(background_color='transparent', color='white', font_size=20, width=40)
        )
        header_box.add(btn_settings)
        
        btn_import = toga.Button(
            "⚡ 导入单词", 
            on_press=self.show_bulk_import_view, 
            style=Pack(background_color='white', color=self.COLOR_PRIMARY, font_weight='bold', margin_left=10)
        )
        header_box.add(btn_import)
        self.study_box.add(header_box)
        
        # Content
        self.study_content = toga.Box(style=Pack(direction=COLUMN, flex=1))
        self.study_box.add(self.study_content)
        
        self.show_dashboard()
        return self.study_box

    def show_dashboard(self):
        self.study_content.clear()
        container = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        total_words = self.db_manager.get_library_word_count(self.current_library_id)
        
        card = toga.Box(style=self.STYLE_CARD)
        card.add(toga.Label("当前进度", style=self.STYLE_SUBTITLE))
        card.add(toga.Label(f"{total_words} 词", style=Pack(font_size=32, font_weight='bold', color=self.COLOR_PRIMARY, margin_top=5)))
        card.add(toga.ProgressBar(max=100, value=0, style=Pack(margin_top=15, flex=1)))
        container.add(card)
        
        btn_start = toga.Button(
            "🚀 开始今日学习", 
            on_press=self.start_learning, 
            style=Pack(
                background_color=self.COLOR_PRIMARY, 
                color='white', 
                font_weight='bold', 
                height=50, 
                margin_top=30
            )
        )
        container.add(btn_start)
        self.study_content.add(container)

    def start_learning(self, widget):
        self.learning_queue = self.db_manager.get_words_by_library(self.current_library_id)
        if not self.learning_queue:
            self.main_window.info_dialog("提示", "当前词库为空，请先导入单词！")
            return
        self.current_word_index = 0
        self.show_next_card()

    def show_next_card(self):
        self.study_content.clear()
        if self.current_word_index >= len(self.learning_queue):
            self.main_window.info_dialog("完成", "本轮学习结束！")
            self.show_dashboard()
            return
        word_data = self.learning_queue[self.current_word_index]
        card = self.WordCard(word_data, on_next_callback=self.next_word)
        self.study_content.add(card)

    def next_word(self):
        self.current_word_index += 1
        self.show_next_card()

    def build_review_tab(self):
        box = toga.Box(style=self.STYLE_ROOT)
        header = toga.Box(style=Pack(padding=15, background_color=self.COLOR_PRIMARY, align_items=CENTER))
        header.add(toga.Label("单词检验", style=Pack(font_size=18, font_weight='bold', color='white')))
        box.add(header)
        
        content = toga.Box(style=Pack(direction=COLUMN, padding=20))
        content.add(toga.Label("选择检验模式", style=self.STYLE_SUBTITLE))
        
        btn_all = toga.Button("全库检验", on_press=lambda w: self.start_quiz('all'), style=self.STYLE_BTN_PRIMARY)
        # Margin fix
        btn_all.style.margin_bottom = 15
        content.add(btn_all)
        
        btn_select = toga.Button("选择单词检验", on_press=lambda w: self.start_quiz('select'), style=self.STYLE_BTN_SECONDARY)
        content.add(btn_select)
        
        box.add(content)
        return box

    def start_quiz(self, mode):
        # mode: 'all' or 'select'
        # BUT user also wants "Choice" or "Spell" mode selection?
        # Let's first select scope, then mode.
        # Or better: "Start Quiz" -> Dialog to choose type?
        # Current UI has buttons for 'all' and 'select'.
        # Let's prompt for quiz type after scope selection (or before).
        
        # New flow:
        # 1. User clicks "全库检验" -> Dialog: "选择模式: [选择题] [默写]"
        # 2. User clicks "选择单词检验" -> Select words -> "开始检验" -> Dialog: "选择模式"
        
        if mode == 'select':
             # Go to selection screen first
            lib = {'id': self.current_library_id, 'name': '选择单词'} 
            self.show_library_detail(lib, selection_mode='quiz')
            return

        # For 'all' or after selection (handled in do_action of detail view? No, detail view calls start_quiz too?)
        # Detail view currently calls app.show_quiz_ui(words) directly.
        # We need to intercept to ask for mode.
        
        # Let's just ask mode here for 'all'
        self.ask_quiz_mode(self.db_manager.get_words_by_library(self.current_library_id))

    def ask_quiz_mode(self, words):
        if not words:
            self.main_window.info_dialog("提示", "没有单词可检验")
            return

        # Custom Dialog to choose mode? Toga doesn't have custom dialogs easily.
        # We can show a temporary view or use QuestionDialog (Yes/No).
        # "选择题 (Yes) / 默写 (No)?" - A bit hacky but works.
        
        def on_result(widget, result):
            mode = 'choice' if result else 'spell'
            self.show_quiz_ui(words, mode)
            
        self.main_window.question_dialog(
            "选择检验模式", 
            "请选择检验方式:\n点击 [Yes] 进入选择题模式\n点击 [No] 进入默写模式",
            on_result=on_result
        )

    def show_quiz_ui(self, words, mode='choice'):
        self.content_area.clear()
        quiz_view = self.QuizView(
            self, 
            words=words, 
            on_finish=lambda w=None: self.switch_tab(1),
            mode=mode
        )
        self.content_area.add(quiz_view)

def main():
    return EasyWordApp()
