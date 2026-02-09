import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..database.manager import db_manager
from ..consts import *

class LibraryDetailView(toga.Box):
    def __init__(self, app, library, on_back, mode='manage'):
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.library = library
        self.on_back = on_back
        self.mode = mode # 'manage' or 'quiz'
        self.selected_word_ids = set()
        self.word_widgets = {} # id -> widget
        self.build_ui()
        
    def build_ui(self):
        # 1. Top Bar
        header = toga.Box(style=Pack(
            direction=ROW, 
            padding=10, 
            background_color=COLOR_PRIMARY,
            align_items=CENTER
        ))
        
        btn_back = toga.Button(
            "⬅", 
            on_press=self.on_back, 
            style=Pack(width=40, height=40, background_color=COLOR_PRIMARY, color='white', font_size=16)
        )
        
        title_text = self.library['name']
        if self.mode == 'quiz':
            title_text = "选择检验单词"
            
        title = toga.Label(
            title_text, 
            style=Pack(flex=1, font_size=18, font_weight='bold', color='white', margin_left=10)
        )
        
        # Add/Import only in manage mode
        if self.mode == 'manage':
            btn_add = toga.Button(
                "+ 导入", 
                on_press=self.go_import,
                style=Pack(background_color=COLOR_ACCENT, color='white', font_weight='bold')
            )
            header.add(btn_back)
            header.add(title)
            header.add(btn_add)
        else:
            header.add(btn_back)
            header.add(title)
            
        self.add(header)
        
        # 2. Search & Toolbar
        toolbar = toga.Box(style=Pack(direction=ROW, padding=10, background_color=COLOR_SURFACE, align_items=CENTER))
        
        self.search_input = toga.TextInput(placeholder="搜索库内单词...", style=Pack(flex=1, margin_right=10))
        btn_search = toga.Button("🔍", on_press=self.do_search, style=Pack(width=40))
        
        toolbar.add(self.search_input)
        toolbar.add(btn_search)
        self.add(toolbar)
        
        # 3. Selection Actions Bar (Hidden by default)
        bg_color = '#FFEBEE' if self.mode == 'manage' else '#E8F5E9' # Red for delete, Green for Quiz
        self.selection_bar = toga.Box(style=Pack(
            direction=ROW, 
            padding=10, 
            background_color=bg_color, 
            height=0 
        ))
        label_color = COLOR_ERROR if self.mode == 'manage' else COLOR_SUCCESS
        self.selection_label = toga.Label("已选 0 项", style=Pack(flex=1, color=label_color, font_weight='bold'))
        
        action_label = "🗑 删除" if self.mode == 'manage' else "🚀 开始检验"
        action_color = COLOR_ERROR if self.mode == 'manage' else COLOR_SUCCESS
        btn_action = toga.Button(
            action_label, 
            on_press=self.do_action, 
            style=Pack(background_color=action_color, color='white')
        )
        
        self.selection_bar.add(self.selection_label)
        self.selection_bar.add(btn_action)
        
        # 4. Word List
        self.scroll = toga.ScrollContainer(style=Pack(flex=1))
        self.list_container = toga.Box(style=Pack(direction=COLUMN, padding=10))
        self.scroll.content = self.list_container
        self.add(self.scroll)
        
        self.refresh_list()

    def refresh_list(self, query=None):
        self.list_container.clear()
        self.word_widgets.clear()
        self.selected_word_ids.clear()
        self.update_selection_bar()
        
        words = db_manager.get_words_by_library(self.library['id'], query)
        
        if not words:
            self.list_container.add(toga.Label("暂无单词，点击右上角导入", style=Pack(padding=20, alignment=CENTER, color=COLOR_TEXT_SECONDARY)))
            return
            
        for word in words:
            item = self.create_word_item(word)
            self.list_container.add(item)
            self.word_widgets[word['id']] = item

    def create_word_item(self, word):
        # Improved Layout:
        # [ Word Info (Clickable for Edit/Detail) ] [ Checkbox ]
        
        row = toga.Box(style=Pack(
            direction=ROW, 
            padding=12, 
            margin_bottom=8, 
            background_color='white',
            align_items=CENTER
        ))
        
        # 1. Word Info Area (Clickable)
        info_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        # Word Text as Button for interaction
        # Note: 'alignment' is not a valid style for Button in Toga. 
        # Removing it. Button text alignment is platform dependent (usually center).
        btn_word = toga.Button(
            word['word'],
            on_press=lambda w, wd=word: self.on_word_click(wd),
            style=Pack(
                background_color='transparent', 
                color=COLOR_TEXT_PRIMARY, 
                font_weight='bold', 
                font_size=16
            )
        )
        info_box.add(btn_word)
        
        if word['definition_cn']:
            defi = word['definition_cn'].replace('\n', ' ')
            if len(defi) > 20: defi = defi[:20] + "..."
            # Definition label (non-interactive, but visually part of the row)
            lbl_def = toga.Label(defi, style=Pack(font_size=12, color=COLOR_TEXT_SECONDARY, margin_left=4))
            info_box.add(lbl_def)
            
        row.add(info_box)
        
        # 2. Checkbox (Right Side)
        # Use a distinct visual style
        is_selected = word['id'] in self.selected_word_ids
        check_char = "☑" if is_selected else "☐"
        check_color = COLOR_PRIMARY if is_selected else COLOR_TEXT_SECONDARY
        
        btn_select = toga.Button(
            check_char, 
            on_press=lambda w, wid=word['id']: self.toggle_selection(wid, w),
            style=Pack(width=45, height=45, background_color='transparent', font_size=20, color=check_color)
        )
        
        row.add(btn_select)
        
        return row

    def on_word_click(self, word):
        # In Manage mode: Edit
        # In Quiz mode: Show detail popup
        if self.mode == 'manage':
            self.app.show_edit_word_view(word, self)
        else:
            self.app.main_window.info_dialog(word['word'], f"{word['definition_cn']}\n\n{word['example']}")

    def toggle_selection(self, word_id, widget):
        if word_id in self.selected_word_ids:
            self.selected_word_ids.remove(word_id)
            widget.text = "☐"
            widget.style.color = COLOR_TEXT_SECONDARY
        else:
            self.selected_word_ids.add(word_id)
            widget.text = "☑"
            widget.style.color = COLOR_PRIMARY
            
        self.update_selection_bar()

    def update_selection_bar(self):
        count = len(self.selected_word_ids)
        if count > 0:
            if self.selection_bar not in self.children:
                self.insert(2, self.selection_bar) # Index 2 is after Toolbar
            self.selection_label.text = f"已选中 {count} 个单词"
        else:
            if self.selection_bar in self.children:
                self.remove(self.selection_bar)

    def do_action(self, widget):
        if not self.selected_word_ids: return
        
        if self.mode == 'manage':
            # Delete
            count = len(self.selected_word_ids)
            if db_manager.delete_words(list(self.selected_word_ids)):
                self.app.main_window.info_dialog("成功", f"已删除 {count} 个单词")
                self.refresh_list()
            else:
                self.app.main_window.info_dialog("错误", "删除失败")
        elif self.mode == 'quiz':
            # Start Quiz
            # Need to get word objects for IDs
            all_words = db_manager.get_words_by_library(self.library['id'])
            selected = [w for w in all_words if w['id'] in self.selected_word_ids]
            
            # Instead of showing UI directly, ask for mode
            self.app.ask_quiz_mode(selected)

    def do_search(self, widget):
        self.refresh_list(self.search_input.value.strip())

    def go_import(self, widget):
        self.app.show_bulk_import_view(library_id=self.library['id'], return_view=self)
