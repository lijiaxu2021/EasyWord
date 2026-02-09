import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..database.manager import db_manager
from ..consts import *

class EditWordView(toga.Box):
    def __init__(self, app, word_data, on_save, on_cancel):
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.word_data = word_data
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.build_ui()
        
    def build_ui(self):
        # Header
        header = toga.Box(style=Pack(
            padding=15, 
            background_color=COLOR_PRIMARY,
            margin_bottom=10,
            direction=ROW,
            align_items=CENTER
        ))
        header.add(toga.Label("编辑单词", style=Pack(font_size=18, font_weight='bold', color='white', flex=1)))
        self.add(header)
        
        # Scrollable Form
        scroll = toga.ScrollContainer(style=Pack(flex=1))
        content = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        content.add(toga.Label("单词拼写", style=STYLE_SUBTITLE))
        self.word_input = toga.TextInput(value=self.word_data['word'], style=STYLE_INPUT)
        content.add(self.word_input)
        
        content.add(toga.Label("音标", style=STYLE_SUBTITLE))
        self.phonetic_input = toga.TextInput(value=self.word_data.get('phonetic', ''), style=STYLE_INPUT)
        content.add(self.phonetic_input)
        
        content.add(toga.Label("中文释义", style=STYLE_SUBTITLE))
        self.cn_input = toga.TextInput(value=self.word_data.get('definition_cn', ''), style=STYLE_INPUT)
        content.add(self.cn_input)
        
        content.add(toga.Label("英文释义", style=STYLE_SUBTITLE))
        self.en_input = toga.TextInput(value=self.word_data.get('definition_en', ''), style=STYLE_INPUT)
        content.add(self.en_input)
        
        content.add(toga.Label("例句", style=STYLE_SUBTITLE))
        self.example_input = toga.MultilineTextInput(value=self.word_data.get('example', ''), style=Pack(height=100, margin_bottom=20, background_color=COLOR_SURFACE))
        content.add(self.example_input)
        
        content.add(toga.Label("分类", style=STYLE_SUBTITLE))
        self.category_input = toga.TextInput(value=self.word_data.get('category', 'General'), style=STYLE_INPUT)
        content.add(self.category_input)
        
        scroll.content = content
        self.add(scroll)
        
        # Actions
        btn_box = toga.Box(style=Pack(direction=ROW, padding=15, background_color=COLOR_SURFACE))
        
        btn_cancel = toga.Button("取消", on_press=self.on_cancel, style=Pack(flex=1, margin_right=10, height=45))
        btn_save = toga.Button("保存修改", on_press=self.do_save, style=STYLE_BTN_PRIMARY)
        
        btn_box.add(btn_cancel)
        btn_box.add(btn_save)
        self.add(btn_box)
        
    def do_save(self, widget):
        word = self.word_input.value.strip()
        if not word:
            self.app.main_window.info_dialog("提示", "单词不能为空")
            return
            
        success = db_manager.update_word(
            word_id=self.word_data['id'],
            word=word,
            definition_cn=self.cn_input.value.strip(),
            phonetic=self.phonetic_input.value.strip(),
            definition_en=self.en_input.value.strip(),
            example=self.example_input.value.strip(),
            category=self.category_input.value.strip()
        )
        
        if success:
            self.on_save()
        else:
            self.app.main_window.info_dialog("错误", "保存失败")