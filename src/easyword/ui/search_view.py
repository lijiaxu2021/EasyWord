import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..consts import *
from ..ai_service import lookup_word_ai
from .word_card import WordCard
import threading

class SearchWordView(toga.Box):
    def __init__(self, app):
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.build_ui()
        
    def build_ui(self):
        # 1. Header
        header = toga.Box(style=Pack(
            direction=ROW, 
            margin=15, 
            background_color=COLOR_PRIMARY,
            align_items=CENTER
        ))
        header.add(toga.Label("查词 & 学习", style=Pack(font_size=18, font_weight='bold', color='white')))
        self.add(header)
        
        # 2. Search Bar
        search_box = toga.Box(style=Pack(
            direction=ROW, 
            margin=20, 
            background_color=COLOR_SURFACE,
            align_items=CENTER
        ))
        
        self.input_search = toga.TextInput(
            placeholder="输入单词...", 
            style=Pack(flex=1, height=45, font_size=16)
        )
        
        self.btn_search = toga.Button(
            "🔍 搜索", 
            on_press=self.do_search, 
            style=Pack(
                width=80, 
                height=45, 
                background_color=COLOR_PRIMARY, 
                color='white', 
                font_weight='bold',
                margin_left=10
            )
        )
        
        search_box.add(self.input_search)
        search_box.add(self.btn_search)
        self.add(search_box)
        
        # 3. Content Area (Result)
        self.content_area = toga.Box(style=Pack(flex=1, direction=COLUMN, margin=10))
        
        # Default State
        self.placeholder_box = toga.Box(style=Pack(flex=1, direction=COLUMN, align_items=CENTER))
        self.placeholder_box.add(toga.Label("输入单词开始学习", style=Pack(font_size=14, color=COLOR_TEXT_SECONDARY)))
        self.content_area.add(self.placeholder_box)
        
        self.add(self.content_area)

    def do_search(self, widget):
        word = self.input_search.value.strip()
        if not word:
            return
            
        # UI Update
        self.btn_search.enabled = False
        self.btn_search.text = "..."
        self.content_area.clear()
        
        loading_label = toga.Label("AI 正在分析中...", style=Pack(margin=20, align_items=CENTER))
        self.content_area.add(loading_label)
        
        def run():
            # 1. Check if word exists in current library?
            # User requirement: "Automatically add to current library".
            # So if it exists, maybe show existing? But user implies "Real-time learn", usually implies fetching new info.
            # Let's try AI lookup first.
            
            print(f"DEBUG: Starting AI lookup for {word}")
            res = lookup_word_ai(word)
            print(f"DEBUG: AI Result: {res}")
            
            def on_complete():
                self.btn_search.enabled = True
                self.btn_search.text = "🔍 搜索"
                self.content_area.clear()
                
                if res:
                    # Save to DB
                    print("DEBUG: Processing AI result...")
                    def_cn = res.get('definition_cn', '')
                    memory_method = res.get('memory_method', '')
                    example = res.get('example', '')
                    phonetic = res.get('phonetic', '')
                    def_en = res.get('definition_en', '')
                    
                    # Ensure strings (AI might return list for examples or definitions)
                    if isinstance(def_cn, list): 
                        def_cn = "\n".join([str(x) for x in def_cn])
                    if isinstance(example, list): 
                        example = "\n".join([str(x) for x in example])
                    if isinstance(memory_method, list):
                        memory_method = "\n".join([str(x) for x in memory_method])
                        
                    # Add/Update word
                    # If exists, update? Or add new?
                    # Schema has UNIQUE(library_id, word).
                    # We should check if exists first to avoid error, or just try add.
                    # Actually, update is better if we want to refresh info.
                    # But for now, let's try add, if fails (exists), we might want to update the memory method if it was empty.
                    
                    # For simplicity: Try Add. If None (exists), Update.
                    lib_id = self.app.current_library_id
                    print(f"DEBUG: Current Library ID: {lib_id}")
                    
                    # Try fetch existing to get ID
                    existing = self.app.db_manager.get_word_by_text(lib_id, word)
                    print(f"DEBUG: Existing word: {existing}")
                    
                    if existing:
                        # Update fields
                        # We need an update method in DB manager.
                        # Assuming we implement update_word_details
                        # For now, let's just show the result. User said "Auto add".
                        # If already exists, it is "in library".
                        self.app.db_manager.update_word_details(
                            existing['id'], 
                            def_cn, phonetic, def_en, example, memory_method
                        )
                        final_word_data = existing
                        final_word_data.update(res) # Overlay new data for display
                    else:
                        new_id = self.app.db_manager.add_word(
                            word=res['word'],
                            definition_cn=def_cn,
                            phonetic=phonetic,
                            definition_en=def_en,
                            example=example,
                            memory_method=memory_method,
                            library_id=lib_id
                        )
                        print(f"DEBUG: New ID: {new_id}")
                        if new_id:
                            final_word_data = res
                            final_word_data['id'] = new_id
                        else:
                            print("DEBUG: Failed to add word to DB")
                            # Try to use dialog instead of deprecated info_dialog
                            self.app.main_window.dialog(toga.InfoDialog("错误", "保存失败 (DB Error)"))
                            return

                    # Show Card
                    # We reuse WordCard, but maybe hide the "Next" button or change its behavior?
                    # WordCard has on_next_callback.
                    # Here, maybe "Next" clears the search?
                    card = WordCard(final_word_data, on_next_callback=lambda: self.input_search.focus())
                    # Change button text? WordCard structure might need access.
                    # WordCard.btn_action text is "Next Word" or "Check Definition".
                    # In Study mode it defaults to "Next Word".
                    # Let's just keep it. Clicking it will trigger callback -> focus input.
                    
                    self.content_area.add(card)
                    
                else:
                    print("DEBUG: AI result is None or Empty")
                    self.content_area.add(toga.Label("查询失败，请重试", style=Pack(margin=20, align_items=CENTER, color=COLOR_ERROR)))

            self.app.loop.call_soon_threadsafe(on_complete)

        threading.Thread(target=run, daemon=True).start()
