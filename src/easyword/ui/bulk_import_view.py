import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..database.manager import db_manager
from ..ai_service import generate_word_info_bulk
from ..consts import *
import threading
import json

class BulkImportView(toga.Box):
    def __init__(self, app, library_id, on_cancel):
        # Use STYLE_ROOT for consistent layout base (flex=1)
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.library_id = library_id
        self.on_cancel = on_cancel
        self.build_ui()
        
    def build_ui(self):
        # 1. Header
        header = toga.Box(style=Pack(
            padding=15, 
            background_color=COLOR_PRIMARY,
            margin_bottom=10
        ))
        header.add(toga.Label("AI 批量导入", style=Pack(font_size=18, font_weight='bold', color='white')))
        header.add(toga.Label(
            "输入任意文本/单词列表，AI 将自动识别并生成详情", 
            style=Pack(font_size=12, color='#E3F2FD', margin_top=5)
        ))
        self.add(header)
        
        # 2. Input Area
        # Use a container for the input to control margins better
        input_container = toga.Box(style=Pack(flex=1, padding_left=15, padding_right=15, padding_bottom=15))
        
        self.input_text = toga.MultilineTextInput(
            placeholder="例如：\napple, banana\nI want to learn computer science.",
            style=STYLE_INPUT
        )
        # Ensure input takes up all space in its container
        self.input_text.style.flex = 1
        self.input_text.style.font_family = 'monospace'
        
        input_container.add(self.input_text)
        self.add(input_container)
        
        # 3. Actions
        btn_box = toga.Box(style=Pack(
            direction=ROW, 
            padding=15, 
            background_color=COLOR_SURFACE,
            align_items=CENTER
        ))
        
        btn_cancel = toga.Button(
            "取消", 
            on_press=self.on_cancel, 
            style=Pack(flex=1, margin_right=10, height=45)
        )
        
        self.btn_analyze = toga.Button(
            "✨ AI 分析并导入", 
            on_press=self.do_analyze, 
            style=STYLE_BTN_PRIMARY
        )
        # Manually set flex/height if style dict doesn't fully cover it in this context
        self.btn_analyze.style.flex = 2
        
        btn_box.add(btn_cancel)
        btn_box.add(self.btn_analyze)
        self.add(btn_box)

    def do_analyze(self, widget):
        text = self.input_text.value.strip()
        if not text:
            self.app.main_window.info_dialog("提示", "请输入文本内容")
            return
            
        self.btn_analyze.enabled = False
        self.btn_analyze.text = "AI 正在分析中..."
        self.input_text.readonly = True
        
        def run():
            results = generate_word_info_bulk(text)
            
            def on_complete():
                self.btn_analyze.enabled = True
                self.btn_analyze.text = "✨ AI 分析并导入"
                self.input_text.readonly = False
                
                if results and isinstance(results, list):
                    count = 0
                    for item in results:
                        word = item.get('word')
                        if word:
                            # Flatten data for simple storage
                            def_cn = item.get('definition_cn')
                            if isinstance(def_cn, list):
                                def_cn = "\n".join(def_cn)
                            
                            ex = item.get('example')
                            if isinstance(ex, list):
                                pass # Already string usually based on prompt
                            
                            res = db_manager.add_word(
                                word=word,
                                definition_cn=def_cn,
                                phonetic=item.get('phonetic', ''),
                                definition_en=item.get('definition_en', ''),
                                example=ex,
                                library_id=self.library_id
                            )
                            if res:
                                count += 1
                    
                    self.app.main_window.info_dialog("完成", f"成功导入 {count} 个单词！")
                    self.on_cancel() # Go back
                else:
                    self.app.main_window.info_dialog("失败", "AI 无法识别内容或网络错误")

            self.app.loop.call_soon_threadsafe(on_complete)

        threading.Thread(target=run, daemon=True).start()
