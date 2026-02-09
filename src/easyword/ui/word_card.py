import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..consts import *

class WordCard(toga.Box):
    def __init__(self, word_data, on_next_callback):
        # Apply new root style
        super().__init__(style=STYLE_ROOT)
        self.word_data = word_data
        self.on_next = on_next_callback
        self.is_flipped = False
        
        self.build_ui()
        
    def build_ui(self):
        # 1. Main Scroll Area
        self.scroll = toga.ScrollContainer(style=Pack(flex=1))
        
        # 2. Content Container (Modern Card Look)
        content = toga.Box(style=Pack(
            direction=COLUMN, 
            padding=20, 
            alignment=CENTER 
        ))
        
        # --- Word Area ---
        word_box = toga.Box(style=Pack(direction=COLUMN, margin_bottom=20, margin_top=10, align_items=CENTER))
        word_box.add(toga.Label(
            self.word_data['word'], 
            style=Pack(font_size=36, font_weight='bold', color=COLOR_PRIMARY_DARK, margin_bottom=5, text_align='center')
        ))
        
        if self.word_data.get('phonetic'):
            word_box.add(toga.Label(
                f"/{self.word_data['phonetic']}/", 
                style=Pack(font_size=16, color=COLOR_ACCENT, font_family='monospace')
            ))
        content.add(word_box)
            
        # --- Details Area (Shown by default in Study Mode) ---
        # Note: If this is Quiz mode, we might want to hide it.
        # But user said: "Left side study mode default show explanation".
        # So we show it immediately.
        self.details_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        # Helper to create sections
        def add_section(title, text, is_example=False):
            box = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15, flex=1)) # flex=1 for width
            # Section Title
            box.add(toga.Label(
                title, 
                style=Pack(font_weight='bold', font_size=13, color=COLOR_TEXT_SECONDARY, margin_bottom=4)
            ))
            # Content
            # line_height is not supported in Pack, removing it.
            # Use MultilineLabel-like behavior? Toga Label wraps if width is constrained.
            # In a ScrollContainer -> Box(COLUMN), width is usually constrained to screen width.
            # Ensure text is not empty
            if not text: return
            
            # For examples, split lines
            if is_example:
                lines = text.split('\n')
                for line in lines:
                    # MultilineLabel to ensure wrapping
                    # Increased height/flex to ensure full visibility
                    box.add(toga.MultilineTextInput(
                        value=line.strip(),
                        readonly=True,
                        style=Pack(
                            font_size=16, 
                            font_style='italic', 
                            color='#455A64', 
                            padding_bottom=4, # Increased spacing
                            flex=1, 
                            min_height=60, # Ensure enough height for 2-3 lines
                            background_color='transparent'
                        )
                    ))
            else:
                # Definition: split by newlines if any for better formatting
                lines = text.split('\n')
                for line in lines:
                    box.add(toga.MultilineTextInput(
                        value=line.strip(),
                        readonly=True,
                        style=Pack(
                            font_size=16, 
                            color=COLOR_TEXT_PRIMARY, 
                            padding_bottom=4, 
                            flex=1, 
                            min_height=40, # Minimum height
                            background_color='transparent'
                        )
                    ))
                    
            self.details_box.add(box)

        # Chinese Definition
        if self.word_data.get('definition_cn'):
            add_section("中文释义", self.word_data['definition_cn'])
            
        # English Definition
        if self.word_data.get('definition_en'):
            add_section("ENGLISH DEFINITION", self.word_data['definition_en'])

        # Example
        if self.word_data.get('example'):
            add_section("EXAMPLE", self.word_data['example'], is_example=True)

        # Memory Method (New)
        if self.word_data.get('memory_method'):
            add_section("记忆方法", self.word_data['memory_method'])
            
        content.add(self.details_box)
        
        self.content_container = content
        self.scroll.content = self.content_container
        self.add(self.scroll)
        
        # 3. Bottom Action Bar
        bottom_bar = toga.Box(style=Pack(
            direction=COLUMN, 
            padding=15, 
            background_color=COLOR_SURFACE, 
            align_items=CENTER
        ))
        
        # In Study Mode (Default show), button is just "Next"
        self.btn_action = toga.Button(
            "下一个单词 →", 
            on_press=self.on_action_click,
            style=STYLE_BTN_PRIMARY
        )
        
        bottom_bar.add(self.btn_action)
        self.add(bottom_bar)

    def on_action_click(self, widget):
        # Always Next
        self.on_next()

