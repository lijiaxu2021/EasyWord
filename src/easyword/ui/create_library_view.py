import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..database.manager import db_manager
from ..consts import *

class CreateLibraryView(toga.Box):
    def __init__(self, app, on_cancel):
        # Use STYLE_ROOT to ensure full screen flex layout
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.on_cancel = on_cancel
        self.build_ui()
        
    def build_ui(self):
        # 1. Header (Consistent with App Theme)
        header = toga.Box(style=Pack(
            padding=15, 
            background_color=COLOR_PRIMARY,
            margin_bottom=20
        ))
        header.add(toga.Label("新建词库", style=Pack(font_size=20, font_weight='bold', color='white')))
        self.add(header)
        
        # 2. Form Content
        # Use a ScrollContainer in case of small screens
        scroll = toga.ScrollContainer(style=Pack(flex=1))
        content = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        content.add(toga.Label("词库名称", style=STYLE_SUBTITLE))
        self.name_input = toga.TextInput(
            placeholder="例如：考研英语、托福核心词...",
            style=STYLE_INPUT
        )
        content.add(self.name_input)
        
        content.add(toga.Label("描述 (可选)", style=STYLE_SUBTITLE))
        self.desc_input = toga.TextInput(
            placeholder="简单描述一下这个词库...",
            style=STYLE_INPUT
        )
        content.add(self.desc_input)
        
        # Add some spacing/illustration maybe?
        content.add(toga.Box(style=Pack(flex=1))) # Spacer
        
        scroll.content = content
        self.add(scroll)
        
        # 3. Action Buttons (Fixed at bottom)
        btn_box = toga.Box(style=Pack(
            direction=ROW, 
            padding=15, 
            background_color=COLOR_SURFACE
        ))
        
        btn_cancel = toga.Button(
            "取消", 
            on_press=self.on_cancel, 
            style=Pack(flex=1, margin_right=10, height=45)
        )
        btn_save = toga.Button(
            "保存", 
            on_press=self.do_save, 
            style=STYLE_BTN_PRIMARY
        )
        
        btn_box.add(btn_cancel)
        btn_box.add(btn_save)
        self.add(btn_box)
        
    def do_save(self, widget):
        name = self.name_input.value.strip()
        if not name:
            self.app.main_window.info_dialog("提示", "请输入词库名称")
            return
            
        desc = self.desc_input.value.strip()
        
        if db_manager.create_library(name, desc):
            self.app.main_window.info_dialog("成功", "词库创建成功")
            self.on_cancel() # Go back
        else:
            self.app.main_window.info_dialog("错误", "创建失败，词库名可能已存在")
