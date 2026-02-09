import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT
from ..database.manager import db_manager
from ..consts import *

class LibraryView(toga.Box):
    def __init__(self, app, on_select_library):
        # Ensure root has flex=1 and correct background
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.on_select_library = on_select_library
        self.build_ui()
        
    def build_ui(self):
        # 1. Top Search Bar (Fixed height, modern look)
        search_container = toga.Box(style=Pack(
            direction=ROW, 
            padding=10, 
            background_color=COLOR_PRIMARY,
            align_items=CENTER
        ))
        
        self.search_input = toga.TextInput(
            placeholder="搜索词库...", 
            style=Pack(flex=1, height=40, background_color='white', margin_right=10)
        )
        # Search icon/button
        btn_search = toga.Button(
            "🔍", 
            on_press=self.do_search, 
            style=Pack(width=45, height=40, background_color=COLOR_ACCENT, color='white')
        )
        
        search_container.add(self.search_input)
        search_container.add(btn_search)
        self.add(search_container)
        
        # 2. Library List (Scrollable, takes remaining space)
        # CRITICAL: ScrollContainer must have flex=1 to take up remaining space
        # without pushing bounds.
        self.scroll = toga.ScrollContainer(style=Pack(flex=1))
        
        # The content inside scroll needs to be a column box
        self.library_list_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        self.scroll.content = self.library_list_box
        self.add(self.scroll)
        
        # 3. Floating Action Button (FAB) Simulation
        # Since Toga doesn't support Z-index overlays easily, we use a bottom bar
        # with a prominent "Add" button.
        footer = toga.Box(style=Pack(
            direction=COLUMN, 
            padding=15, 
            background_color=COLOR_SURFACE
        ))
        
        btn_add = toga.Button(
            "+ 新建词库", 
            on_press=self.show_create_dialog, 
            style=STYLE_BTN_PRIMARY
        )
        footer.add(btn_add)
        self.add(footer)
        
        self.refresh_list()

    def refresh_list(self, query=None):
        self.library_list_box.clear()
        
        if query:
            libs = db_manager.search_libraries(query)
        else:
            libs = db_manager.get_libraries()
            
        for lib in libs:
            item = self.create_library_item(lib)
            self.library_list_box.add(item)

    def create_library_item(self, lib):
        count = db_manager.get_library_word_count(lib['id'])
        
        # Modern Card Style for Items
        card = toga.Box(style=Pack(
            direction=COLUMN, 
            padding=15, 
            margin_bottom=12, 
            background_color='white',
            # Border radius simulation via transparent borders not possible, 
            # relying on clean spacing and contrast.
        ))
        
        # Header Row: Icon + Name
        row1 = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=5))
        # Emoji as icon
        row1.add(toga.Label("📚", style=Pack(font_size=20, margin_right=10)))
        row1.add(toga.Label(lib['name'], style=Pack(font_weight='bold', font_size=18, flex=1, color=COLOR_TEXT_PRIMARY)))
        
        # Badge for count
        count_label = toga.Label(
            f"{count} 词", 
            style=Pack(
                background_color=COLOR_BACKGROUND, 
                color=COLOR_PRIMARY, 
                font_size=12, 
                padding_top=4, 
                padding_bottom=4,
                padding_left=8,
                padding_right=8
            )
        )
        row1.add(count_label)
        card.add(row1)
        
        # Description
        if lib['description']:
            card.add(toga.Label(
                lib['description'], 
                style=Pack(color=COLOR_TEXT_SECONDARY, font_size=13, margin_bottom=10)
            ))
            
        # Action Bar (Enter)
        # Make the whole card clickable? Toga doesn't support tap on Box easily.
        # We use a full-width flat button at bottom or just a button.
        btn_enter = toga.Button(
            "进入学习 →", 
            on_press=lambda w: self.on_select_library(lib),
            style=Pack(
                background_color='#E3F2FD', # Very light blue
                color=COLOR_PRIMARY,
                height=35,
                font_weight='bold',
                flex=1
            )
        )
        card.add(btn_enter)
        
        return card

    def do_search(self, widget):
        query = self.search_input.value.strip()
        self.refresh_list(query)

    def show_create_dialog(self, widget):
        self.app.show_create_library_view()
