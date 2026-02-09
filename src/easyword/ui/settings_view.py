import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..consts import *

class LogListView(toga.Box):
    def __init__(self, app, on_back):
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.on_back = on_back
        self.build_ui()

    def build_ui(self):
        # Header
        header = toga.Box(style=Pack(direction=ROW, padding=15, background_color=COLOR_PRIMARY, align_items=CENTER))
        btn_back = toga.Button("⬅", on_press=self.on_back, style=Pack(color='white', background_color='transparent', font_weight='bold'))
        header.add(btn_back)
        header.add(toga.Label("系统日志", style=Pack(flex=1, font_size=18, font_weight='bold', color='white', margin_left=10)))
        self.add(header)

        # List
        self.scroll = toga.ScrollContainer(style=Pack(flex=1))
        self.content = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        files = self.app.logger.get_log_files()
        if not files:
            self.content.add(toga.Label("暂无日志", style=Pack(padding=20, alignment=CENTER)))
        else:
            for f in files:
                btn = toga.Button(
                    f"📄 {f}",
                    on_press=lambda w, fn=f: self.show_log_content(fn),
                    style=Pack(margin_bottom=10, height=50, background_color='white')
                )
                self.content.add(btn)
                
        self.scroll.content = self.content
        self.add(self.scroll)

    def show_log_content(self, filename):
        content = self.app.logger.get_log_content(filename)
        self.app.show_log_detail(filename, content, self)

class LogDetailView(toga.Box):
    def __init__(self, app, filename, content, on_back):
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.filename = filename
        self.log_content = content
        self.on_back = on_back
        self.build_ui()

    def build_ui(self):
        # Header
        header = toga.Box(style=Pack(direction=ROW, padding=15, background_color=COLOR_PRIMARY, align_items=CENTER))
        btn_back = toga.Button("⬅", on_press=self.on_back, style=Pack(color='white', background_color='transparent', font_weight='bold'))
        header.add(btn_back)
        header.add(toga.Label(self.filename, style=Pack(flex=1, font_size=16, color='white', margin_left=10)))
        
        # Copy Button
        # Toga doesn't have system clipboard access easily on all platforms yet without 3rd party.
        # But MultilineTextInput usually supports native selection and copy.
        # If user says "cannot copy", maybe it's because readonly=True disables interaction on some platforms?
        # Let's try making it NOT readonly but ignore edits? Or just rely on user selecting text.
        # Or maybe the layout prevents selection.
        # Let's try to add a "Select All" button that focuses the text input?
        
        self.add(header)

        # Text Area
        # Removed readonly=True to potentially allow selection/copy on Android
        # If readonly is True, Android might disable selection.
        # We'll rely on the fact that saving isn't implemented here, so edits are temporary/ignored.
        
        self.text_input = toga.MultilineTextInput(
            value=self.log_content, 
            readonly=False, # Changed to False to allow selection
            style=Pack(flex=1, font_family='monospace', font_size=10)
        )
        self.add(self.text_input)
