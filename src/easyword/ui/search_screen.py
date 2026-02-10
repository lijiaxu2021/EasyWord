from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
import threading
from easyword.ai_service import lookup_word_ai
from easyword.database.manager import db_manager
from easyword.ui.study_screen import WordCard # Reuse WordCard

class SearchScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        self.layout.add_widget(MDLabel(
            text="AI 查词", 
            halign="center", 
            theme_text_color="Primary", 
            font_style="H5",
            size_hint_y=None,
            height=50
        ))
        
        # Search Bar
        search_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        
        self.input_search = MDTextField(
            hint_text="输入单词...",
            mode="rectangle",
            size_hint_x=0.8
        )
        self.input_search.bind(on_text_validate=self.do_search)
        
        btn_search = MDIconButton(
            icon="magnify",
            on_release=self.do_search,
            pos_hint={'center_y': 0.5}
        )
        
        search_box.add_widget(self.input_search)
        search_box.add_widget(btn_search)
        self.layout.add_widget(search_box)
        
        # Content Area
        self.content_container = MDBoxLayout(orientation='vertical', size_hint=(1, 1))
        self.content_container.add_widget(MDLabel(text="输入单词开始 AI 学习", halign="center", theme_text_color="Hint"))
        
        self.layout.add_widget(self.content_container)
        self.add_widget(self.layout)

    def do_search(self, instance):
        word = self.input_search.text.strip()
        if not word:
            return
            
        # UI Update
        self.content_container.clear_widgets()
        self.content_container.add_widget(MDLabel(text="AI 正在深度分析中...", halign="center", theme_text_color="Primary"))
        self.input_search.disabled = True
        
        threading.Thread(target=self.run_search, args=(word,), daemon=True).start()

    def run_search(self, word):
        res = lookup_word_ai(word)
        Clock.schedule_once(lambda dt: self.on_search_complete(res, word))

    def on_search_complete(self, res, word):
        self.input_search.disabled = False
        self.content_container.clear_widgets()
        
        if res:
            # Save to DB
            def_cn = res.get('definition_cn', '')
            memory_method = res.get('memory_method', '')
            example = res.get('example', '')
            phonetic = res.get('phonetic', '')
            def_en = res.get('definition_en', '')
            
            # Ensure strings
            if isinstance(def_cn, list): def_cn = "\n".join([str(x) for x in def_cn])
            if isinstance(example, list): example = "\n".join([str(x) for x in example])
            if isinstance(memory_method, list): memory_method = "\n".join([str(x) for x in memory_method])
            
            # DB Operation
            lib_id = 1 # Default library
            existing = db_manager.get_word_by_text(lib_id, word)
            
            if existing:
                db_manager.update_word_details(
                    existing['id'], def_cn, phonetic, def_en, example, memory_method
                )
                final_word_data = existing
                final_word_data.update(res)
            else:
                new_id = db_manager.add_word(
                    word=res['word'],
                    definition_cn=def_cn,
                    phonetic=phonetic,
                    definition_en=def_en,
                    example=example,
                    memory_method=memory_method,
                    library_id=lib_id
                )
                if new_id:
                    final_word_data = res
                    final_word_data['id'] = new_id
                else:
                    self.content_container.add_widget(MDLabel(text="保存失败", halign="center", theme_text_color="Error"))
                    return

            # Show Card
            self.show_result_card(final_word_data)
        else:
            self.content_container.add_widget(MDLabel(text="查询失败，请重试", halign="center", theme_text_color="Error"))

    def show_result_card(self, word_data):
        # We reuse the logic from StudyScreen but maybe a static card view
        # Or just use the same card class but manually instantiated
        # WordCard in study_screen.py is an MDCard subclass.
        # We can reuse it!
        
        card = WordCard(
            orientation='vertical',
            padding=20,
            spacing=10,
            radius=[15, 15, 15, 15],
            elevation=2,
            size_hint=(1, 1) # Take full space
        )
        
        # We need to set properties manually or create a method in WordCard to populate?
        # WordCard properties are Kivy properties.
        # Let's just manually populate like StudyScreen does, or refactor StudyScreen to use the class better.
        # In StudyScreen, I didn't actually use the WordCard class fully effectively (I added widgets manually in show_word).
        # Let's copy that logic for now to ensure it looks the same.
        
        # Word
        card.add_widget(MDLabel(
            text=word_data['word'], 
            halign="center", 
            font_style="H3",
            theme_text_color="Primary",
            size_hint_y=None,
            height=60
        ))
        
        if word_data.get('phonetic'):
            card.add_widget(MDLabel(
                text=f"/{word_data['phonetic']}/", 
                halign="center", 
                theme_text_color="Secondary",
                font_style="Subtitle1",
                size_hint_y=None,
                height=30
            ))
            
        details_scroll = MDScrollView()
        details_box = MDBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        details_box.bind(minimum_height=details_box.setter('height'))
        
        details_box.add_widget(MDLabel(text="[b]中文释义[/b]", markup=True, theme_text_color="Primary"))
        details_box.add_widget(MDLabel(text=word_data['definition_cn'], theme_text_color="Secondary", adaptive_height=True))
        
        if word_data.get('memory_method'):
            details_box.add_widget(MDLabel(text="\n[b]记忆方法[/b]", markup=True, theme_text_color="Primary"))
            details_box.add_widget(MDLabel(text=word_data['memory_method'], theme_text_color="Secondary", adaptive_height=True))

        if word_data.get('example'):
            details_box.add_widget(MDLabel(text="\n[b]例句[/b]", markup=True, theme_text_color="Primary"))
            details_box.add_widget(MDLabel(text=word_data['example'], theme_text_color="Secondary", font_style="Caption", adaptive_height=True))

        details_scroll.add_widget(details_box)
        card.add_widget(details_scroll)
        
        self.content_container.add_widget(card)
