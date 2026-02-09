import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from ..consts import *
import random

class QuizView(toga.Box):
    def __init__(self, app, words, on_finish, mode='choice'):
        super().__init__(style=STYLE_ROOT)
        self.app = app
        self.words = words
        self.on_finish = on_finish
        self.mode = mode # 'choice' or 'spell'
        self.current_index = 0
        self.correct_count = 0
        self.wrong_count = 0
        
        # Shuffle words for quiz
        random.shuffle(self.words)
        
        self.build_ui()
        self.show_next_question()
        
    def build_ui(self):
        # 1. Header (Progress)
        header = toga.Box(style=Pack(
            direction=ROW, 
            padding=15, 
            background_color=COLOR_PRIMARY,
            align_items=CENTER
        ))
        
        self.progress_label = toga.Label(
            f"进度: 0/{len(self.words)}", 
            style=Pack(font_size=16, font_weight='bold', color='white', flex=1)
        )
        
        btn_exit = toga.Button(
            "退出", 
            on_press=self.do_finish, 
            style=Pack(background_color='transparent', color='white', font_weight='bold')
        )
        
        header.add(self.progress_label)
        header.add(btn_exit)
        self.add(header)
        
        # 2. Question Area
        self.content_container = toga.Box(style=Pack(flex=1, direction=COLUMN, padding=20, alignment=CENTER))
        self.add(self.content_container)

    def show_next_question(self):
        self.content_container.clear()
        
        if self.current_index >= len(self.words):
            self.show_result()
            return
            
        word_data = self.words[self.current_index]
        self.progress_label.text = f"进度: {self.current_index + 1}/{len(self.words)}"
        
        if self.mode == 'choice':
            self.build_choice_question(word_data)
        elif self.mode == 'spell':
            self.build_spell_question(word_data)

    def build_choice_question(self, word_data):
        # Question Card
        question_box = toga.Box(style=Pack(
            direction=COLUMN, 
            background_color='white', 
            padding=20, 
            margin_bottom=20,
            alignment=CENTER
        ))
        
        question_box.add(toga.Label(
            word_data['word'], 
            style=Pack(font_size=32, font_weight='bold', color=COLOR_PRIMARY_DARK, margin_bottom=10, text_align='center')
        ))
        
        if word_data.get('phonetic'):
            question_box.add(toga.Label(
                f"/{word_data['phonetic']}/", 
                style=Pack(font_size=16, color=COLOR_ACCENT, font_family='monospace', margin_bottom=20)
            ))
            
        self.content_container.add(question_box)
        
        # Options
        options = self.generate_options(word_data)
        
        for idx, option in enumerate(options):
            is_correct = (option['id'] == word_data['id'])
            # Truncate and clean definition
            def_text = option['definition_cn'].split('\n')[0]
            if len(def_text) > 25: def_text = def_text[:25] + "..."
            
            btn = toga.Button(
                f"{['A','B','C','D'][idx]}. {def_text}",
                on_press=lambda w, correct=is_correct: self.check_answer(correct),
                style=Pack(
                    margin_bottom=10, 
                    height=50, 
                    background_color='white', 
                    color=COLOR_TEXT_PRIMARY,
                    font_weight='bold'
                )
            )
            self.content_container.add(btn)

    def build_spell_question(self, word_data):
        # Question: Definition -> Input Word
        question_box = toga.Box(style=Pack(
            direction=COLUMN, 
            background_color='white', 
            padding=20, 
            margin_bottom=20,
            alignment=CENTER
        ))
        
        question_box.add(toga.Label(
            "请拼写单词", 
            style=Pack(font_size=14, color=COLOR_TEXT_SECONDARY, margin_bottom=10)
        ))
        
        # Show definition
        def_text = word_data['definition_cn']
        question_box.add(toga.Label(
            def_text, 
            style=Pack(font_size=18, font_weight='bold', color=COLOR_TEXT_PRIMARY, margin_bottom=20, text_align='center')
        ))
        
        self.content_container.add(question_box)
        
        # Input
        self.input_spell = toga.TextInput(placeholder="输入单词...", style=Pack(width=200, margin_bottom=20))
        self.content_container.add(self.input_spell)
        
        # Submit
        btn_submit = toga.Button(
            "确定",
            on_press=lambda w: self.check_spell_answer(word_data),
            style=STYLE_BTN_PRIMARY
        )
        self.content_container.add(btn_submit)

    def generate_options(self, correct_word):
        options = [correct_word]
        wrong_candidates = [w for w in self.words if w['id'] != correct_word['id']]
        
        if len(wrong_candidates) < 3:
            others = wrong_candidates
        else:
            others = random.sample(wrong_candidates, min(3, len(wrong_candidates)))
            
        options.extend(others)
        random.shuffle(options)
        return options

    def check_answer(self, is_correct):
        if is_correct:
            self.correct_count += 1
        else:
            self.wrong_count += 1
        self.current_index += 1
        self.show_next_question()

    def check_spell_answer(self, word_data):
        user_input = self.input_spell.value.strip().lower()
        correct_word = word_data['word'].strip().lower()
        
        if user_input == correct_word:
            self.correct_count += 1
            # Simple feedback?
        else:
            self.wrong_count += 1
            # Ideally show correct answer dialog, but for flow speed we just move on or toast
            # Toga toast not available, use dialog? No, interrupts flow.
            # Let's just move on for now or add a "Result" step.
            
        self.current_index += 1
        self.show_next_question()

    def show_result(self):
        self.content_container.clear()
        
        result_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=20))
        
        result_box.add(toga.Label(
            "检验完成!", 
            style=Pack(font_size=24, font_weight='bold', color=COLOR_PRIMARY, margin_bottom=20)
        ))
        
        result_box.add(toga.Label(
            f"正确: {self.correct_count}", 
            style=Pack(font_size=18, color=COLOR_SUCCESS, margin_bottom=10)
        ))
        
        result_box.add(toga.Label(
            f"错误: {self.wrong_count}", 
            style=Pack(font_size=18, color=COLOR_ERROR, margin_bottom=30)
        ))
        
        btn_finish = toga.Button(
            "返回", 
            on_press=self.do_finish, 
            style=STYLE_BTN_PRIMARY
        )
        
        result_box.add(btn_finish)
        self.content_container.add(result_box)

    def do_finish(self, widget):
        self.on_finish()
