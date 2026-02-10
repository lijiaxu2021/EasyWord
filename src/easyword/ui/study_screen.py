from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from easyword.database.manager import db_manager
import random

class WordCard(MDCard):
    word = StringProperty("")
    phonetic = StringProperty("")
    definition_cn = StringProperty("")
    definition_en = StringProperty("")
    example = StringProperty("")
    memory_method = StringProperty("")
    show_details = BooleanProperty(False)

    def toggle_details(self):
        self.show_details = not self.show_details

class StudyScreen(MDScreen):
    container = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words = []
        self.current_index = 0
        self.build_ui()
        
    def build_ui(self):
        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        self.header = MDLabel(
            text="今日学习", 
            halign="center", 
            theme_text_color="Primary", 
            font_style="H5",
            size_hint_y=None,
            height=50
        )
        self.layout.add_widget(self.header)
        
        # Card Container
        self.card_container = MDBoxLayout(orientation='vertical', size_hint=(1, 1))
        self.layout.add_widget(self.card_container)
        
        # Controls
        self.controls = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=20, padding=[20, 0])
        self.btn_show = MDRaisedButton(text="查看答案", on_release=self.show_answer, size_hint_x=0.5)
        self.btn_next = MDRaisedButton(text="下一个", on_release=self.next_word, size_hint_x=0.5)
        
        self.controls.add_widget(self.btn_show)
        self.controls.add_widget(self.btn_next)
        self.layout.add_widget(self.controls)
        
        self.add_widget(self.layout)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        # Fetch words from DB (default library for now)
        # TODO: Support library selection in Study Mode
        self.words = db_manager.get_words_by_library(1) # Library 1 default
        if not self.words:
            self.show_empty_state()
        else:
            # Shuffle for random study
            random.shuffle(self.words)
            self.current_index = 0
            self.show_word(self.words[self.current_index])

    def show_empty_state(self):
        self.card_container.clear_widgets()
        self.card_container.add_widget(MDLabel(text="当前词库为空，请先导入单词！", halign="center"))
        self.btn_show.disabled = True
        self.btn_next.disabled = True

    def show_word(self, word_data):
        self.card_container.clear_widgets()
        
        # Simple Card UI construction in Python (KV is cleaner but this works)
        # Front: Word + Phonetic
        # Back: Definitions (Hidden initially)
        
        self.current_word_data = word_data
        
        # Card
        card = MDCard(
            orientation='vertical',
            padding=20,
            spacing=10,
            radius=[15, 15, 15, 15],
            elevation=2
        )
        
        # Word
        card.add_widget(MDLabel(
            text=word_data['word'], 
            halign="center", 
            font_style="H3",
            theme_text_color="Primary",
            size_hint_y=None,
            height=60
        ))
        
        # Phonetic
        if word_data.get('phonetic'):
            card.add_widget(MDLabel(
                text=f"/{word_data['phonetic']}/", 
                halign="center", 
                theme_text_color="Secondary",
                font_style="Subtitle1",
                size_hint_y=None,
                height=30
            ))
            
        # Details Container (Scrollable)
        self.details_scroll = MDScrollView()
        self.details_box = MDBoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        self.details_box.bind(minimum_height=self.details_box.setter('height'))
        
        # Definition CN
        self.details_box.add_widget(MDLabel(text="[b]中文释义[/b]", markup=True, theme_text_color="Primary"))
        self.details_box.add_widget(MDLabel(text=word_data['definition_cn'], theme_text_color="Secondary", adaptive_height=True))
        
        # Memory Method
        if word_data.get('memory_method'):
            self.details_box.add_widget(MDLabel(text="\n[b]记忆方法[/b]", markup=True, theme_text_color="Primary"))
            self.details_box.add_widget(MDLabel(text=word_data['memory_method'], theme_text_color="Secondary", adaptive_height=True))

        # Example
        if word_data.get('example'):
            self.details_box.add_widget(MDLabel(text="\n[b]例句[/b]", markup=True, theme_text_color="Primary"))
            self.details_box.add_widget(MDLabel(text=word_data['example'], theme_text_color="Secondary", font_style="Caption", adaptive_height=True))

        self.details_scroll.add_widget(self.details_box)
        
        # Initially hide details
        self.details_scroll.opacity = 0
        self.details_scroll.disabled = True
        
        card.add_widget(self.details_scroll)
        self.card_container.add_widget(card)
        
        self.btn_show.disabled = False
        self.btn_next.disabled = False
        self.details_visible = False

    def show_answer(self, instance):
        if not self.details_visible:
            self.details_scroll.opacity = 1
            self.details_scroll.disabled = False
            self.details_visible = True
        else:
            # Maybe toggle back? No, usually just show.
            pass

    def next_word(self, instance):
        self.current_index += 1
        if self.current_index >= len(self.words):
            self.current_index = 0 # Loop back or finish
            # Show "Finish" toast?
            
        self.show_word(self.words[self.current_index])
