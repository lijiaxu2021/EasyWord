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
            self.app.main_window.dialog(toga.InfoDialog("请稍候", "AI 正在分批分析您的文本，这可能需要一两分钟..."))
            
            # Use the new chunked processing function
            words_data = generate_word_info_bulk(text)
            
            def on_complete():
                self.btn_analyze.enabled = True
                self.btn_analyze.text = "✨ AI 分析并导入"
                
                if words_data:
                    count = 0
                    for w in words_data:
                        # ... (existing insertion logic)
                        # Ensure string format
                        def_cn = w.get('definition_cn', '')
                        if isinstance(def_cn, list): def_cn = "\n".join([str(x) for x in def_cn])
                        example = w.get('example', '')
                        if isinstance(example, list): example = "\n".join([str(x) for x in example])
                        memory_method = w.get('memory_method', '')
                        if isinstance(memory_method, list): memory_method = "\n".join([str(x) for x in memory_method])

                        # Check exist
                        if not self.app.db_manager.get_word_by_text(self.app.current_library_id, w['word']):
                            self.app.db_manager.add_word(
                                word=w['word'],
                                definition_cn=def_cn,
                                phonetic=w.get('phonetic', ''),
                                definition_en=w.get('definition_en', ''),
                                example=example,
                                memory_method=memory_method,
                                library_id=self.app.current_library_id
                            )
                            count += 1
                            
                    self.app.main_window.dialog(toga.InfoDialog("完成", f"成功导入 {count} 个单词！"))
                    self.on_cancel() # Go back
                else:
                    self.app.main_window.dialog(toga.InfoDialog("失败", "AI 无法识别内容或网络错误，请重试"))

            self.app.loop.call_soon_threadsafe(on_complete)

        threading.Thread(target=run, daemon=True).start()
