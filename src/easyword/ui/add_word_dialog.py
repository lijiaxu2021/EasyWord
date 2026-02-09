import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..database.manager import db_manager
from ..consts import *
from ..ai_service import generate_word_info
import threading

# Android-compatible Add Word UI
# Instead of a Window, we'll use a Box that can be shown in the main content area

class AddWordView:
    def __init__(self, app, on_success_callback, on_cancel_callback):
        self.app = app
        self.on_success = on_success_callback
        self.on_cancel = on_cancel_callback
        self.build_ui()

    def build_ui(self):
        # Main container
        self.box = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color=COLOR_BACKGROUND))
        
        # Scrollable content for smaller screens
        scroll = toga.ScrollContainer(horizontal=False, style=Pack(flex=1))
        content_box = toga.Box(style=Pack(direction=COLUMN, margin=15))
        
        # Header
        content_box.add(toga.Label("添加新单词", style=STYLE_HEADING))
        
        # Word Input
        content_box.add(toga.Label("单词:", style=STYLE_SUBTITLE))
        input_row = toga.Box(style=Pack(direction=ROW, margin_bottom=10))
        self.word_input = toga.TextInput(style=Pack(flex=1, margin_right=5))
        self.btn_ai = toga.Button("✨ AI 生成", on_press=self.do_ai_generate, style=Pack(width=100, background_color=COLOR_SECONDARY))
        input_row.add(self.word_input)
        input_row.add(self.btn_ai)
        content_box.add(input_row)

        # Fields
        self.phonetic_input = self.create_field(content_box, "音标:")
        self.cn_input = self.create_field(content_box, "中文释义:")
        self.en_input = self.create_field(content_box, "英文释义:")
        self.example_input = self.create_field(content_box, "例句:", multiline=True)
        self.category_input = self.create_field(content_box, "分类:", default="General")
        
        scroll.content = content_box
        self.box.add(scroll)

        # Actions (Fixed at bottom)
        btn_box = toga.Box(style=Pack(direction=ROW, margin=10, align_items=CENTER))
        btn_cancel = toga.Button("取消", on_press=self.on_cancel, style=Pack(flex=1, margin_right=5, height=40))
        btn_save = toga.Button("保存", on_press=self.do_save, style=STYLE_BTN_PRIMARY)
        # Apply flex=1 to save button manually since style dict doesn't have it
        btn_save.style.flex = 1
        
        btn_box.add(btn_cancel)
        btn_box.add(btn_save)
        self.box.add(btn_box)

    def create_field(self, parent, label, default="", multiline=False):
        parent.add(toga.Label(label, style=STYLE_SUBTITLE))
        if multiline:
            inp = toga.MultilineTextInput(value=default, style=Pack(height=80, margin_bottom=10))
        else:
            inp = toga.TextInput(value=default, style=Pack(margin_bottom=10))
        parent.add(inp)
        return inp

    def do_ai_generate(self, widget):
        word = self.word_input.value.strip()
        if not word:
            self.app.main_window.info_dialog("提示", "请输入单词")
            return
            
        self.btn_ai.enabled = False
        self.btn_ai.text = "生成中..."
        
        def run():
            info = generate_word_info(word)
            if info:
                def update_ui():
                    self.phonetic_input.value = info.get("phonetic", "")
                    self.cn_input.value = info.get("definition_cn", "")
                    self.en_input.value = info.get("definition_en", "")
                    self.example_input.value = info.get("example", "")
                    self.btn_ai.enabled = True
                    self.btn_ai.text = "✨ AI 生成"
                self.app.loop.call_soon_threadsafe(update_ui)
            else:
                def fail():
                    self.app.main_window.info_dialog("错误", "AI 生成失败，请检查网络或 Key")
                    self.btn_ai.enabled = True
                    self.btn_ai.text = "✨ AI 生成"
                self.app.loop.call_soon_threadsafe(fail)

        threading.Thread(target=run, daemon=True).start()

    def do_save(self, widget):
        word = self.word_input.value.strip()
        if not word:
            return
            
        word_id = db_manager.add_word(
            word=word,
            definition_cn=self.cn_input.value,
            phonetic=self.phonetic_input.value,
            definition_en=self.en_input.value,
            example=self.example_input.value,
            category=self.category_input.value
        )
        
        if word_id:
            self.on_success()
        else:
            self.app.main_window.info_dialog("错误", "保存失败，单词可能已存在")
