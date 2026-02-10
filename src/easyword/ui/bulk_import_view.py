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
        input_container = toga.Box(style=Pack(flex=1, direction=COLUMN, padding=15))
        
        self.input_text = toga.MultilineTextInput(
            placeholder="例如：\napple, banana\nI want to learn computer science.",
            style=Pack(flex=1, font_family='monospace', margin_bottom=10)
        )
        input_container.add(self.input_text)
        
        # Log/Progress Area (Scrollable)
        self.log_area = toga.MultilineTextInput(
            readonly=True,
            style=Pack(height=120, font_family='monospace', font_size=10, background_color='#F5F5F5')
        )
        input_container.add(self.log_area)
        
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
        self.btn_analyze.style.flex = 2
        
        btn_box.add(btn_cancel)
        btn_box.add(self.btn_analyze)
        self.add(btn_box)

    def log(self, message):
        self.log_area.value += f"{message}\n"
        self.log_area.scroll_to_bottom()

    def do_analyze(self, widget):
        text = self.input_text.value.strip()
        if not text:
            self.app.main_window.dialog(toga.InfoDialog("提示", "请输入文本内容"))
            return
            
        self.btn_analyze.enabled = False
        self.btn_analyze.text = "AI 正在分析中..."
        self.log_area.value = "任务开始...\n"
        
        def run():
            try:
                # Step 1: Extraction (First log)
                self.app.loop.call_soon_threadsafe(lambda: self.log("正在提取单词列表..."))
                
                # generate_word_info_bulk is now a generator
                total_added = 0
                
                # Iterate over the generator
                for chunk_data in generate_word_info_bulk(text):
                    if not chunk_data: continue
                    
                    self.app.loop.call_soon_threadsafe(lambda: self.log(f"收到分析数据 ({len(chunk_data)} 个)..."))
                    
                    chunk_count = 0
                    for w in chunk_data:
                        # Ensure string format (Double safety)
                        def_cn = str(w.get('definition_cn', ''))
                        example = str(w.get('example', ''))
                        memory_method = str(w.get('memory_method', ''))
                        phonetic = str(w.get('phonetic', ''))
                        def_en = str(w.get('definition_en', ''))
                        word = str(w.get('word', ''))

                        # Check exist
                        if not self.app.db_manager.get_word_by_text(self.app.current_library_id, word):
                            self.app.db_manager.add_word(
                                word=word,
                                definition_cn=def_cn,
                                phonetic=phonetic,
                                definition_en=def_en,
                                example=example,
                                memory_method=memory_method,
                                library_id=self.app.current_library_id
                            )
                            chunk_count += 1
                            self.app.loop.call_soon_threadsafe(lambda w=word: self.log(f"  + {w}"))
                        else:
                            self.app.loop.call_soon_threadsafe(lambda w=word: self.log(f"  = {w} (已存在)"))
                            
                    total_added += chunk_count
                    self.app.loop.call_soon_threadsafe(lambda c=chunk_count: self.log(f"本批入库: {c}"))

                def on_finish():
                    self.btn_analyze.enabled = True
                    self.btn_analyze.text = "✨ AI 分析并导入"
                    self.app.main_window.dialog(toga.InfoDialog("完成", f"任务结束，共导入 {total_added} 个新单词！"))
                    
                self.app.loop.call_soon_threadsafe(on_finish)
                
            except Exception as e:
                print(f"Import Error: {e}")
                def on_error():
                    self.btn_analyze.enabled = True
                    self.btn_analyze.text = "✨ AI 分析并导入"
                    self.log(f"错误: {e}")
                    self.app.main_window.dialog(toga.InfoDialog("错误", "处理过程中发生异常"))
                self.app.loop.call_soon_threadsafe(on_error)

        threading.Thread(target=run, daemon=True).start()
