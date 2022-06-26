
from kivy.uix.widget import Widget
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty
from kivy.core.clipboard import Clipboard

from kivymd.uix.snackbar import Snackbar

import app_values

class Page(Widget):
    page = NumericProperty(5)
    selection = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.copping = False
        self.bubble = None

    @property
    def root_screen(self):
        """returns screen named 'reader' or None"""
        widget = self
        while widget.parent != None:
            if 'name' in dir(widget.parent) and widget.parent.name == 'reader':
                return widget.parent
            widget = widget.parent
        return None

    def on_touch_down(self, touch):
        if self.root_screen.ids.page_presenter.ids.page_back.collide_point(*touch.pos):
            return False
        if self.root_screen.ids.page_presenter.ids.page_forward.collide_point(*touch.pos):
            return False
        if self.copping:
            if not self.bubble.collide_point(*touch.pos):
                self.copping = False
                self.remove_widget(self.bubble)
                return True
        self.deselect()
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.copping:
            if not self.bubble.collide_point(*touch.pos):
                self.copping = False
                self.remove_widget(self.bubble)
                if self.selection:
                    self.deselect()
                return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.selection:
            text = ''
            for child in self.ids.page_content.children:
                # boxlayout keeps his child widgets in reversed order
                text = child.get_selected_text() + text

            def cancel(arg=None):
                self.copping = False
                self.remove_widget(bubble)
                self.deselect()

            def copy(arg=None):
                cancel()
                Clock.schedule_once(lambda dt: self.copy_text(text))

            def translate(arg=...):
                cancel()
                Clock.schedule_once(lambda dt: self.root_screen.present(text))
                
            if not self.copping:
                bubble = Bubble(pos=touch.pos, background_color=(0,0,0,1), orientation='vertical')
                bubble.add_widget(BubbleButton(text='Копировать', on_press=copy))
                bubble.add_widget(BubbleButton(text='Отмена', on_press=cancel))
                bubble.add_widget(BubbleButton(text='Перевод', on_press=translate))
                bubble.pos[0] = max(bubble.pos[0] - bubble.width/2, 5)
                self.bubble = bubble
                self.add_widget(bubble)
                self.copping = True
        return super().on_touch_up(touch)
    
    def copy_text(self, text):
        Clipboard.copy(text)
        snack = Snackbar(
            text = 'Текст скопирован буфер обмена',
            snackbar_x="10dp",
            snackbar_y="10dp",
            snackbar_animation_dir='Right',
            bg_color=(0, 0, 1, 0.4),
        )
        snack.size_hint_x = (self.width - snack.snackbar_x * 2) / self.width
        snack.open()

    def prepare(self):
        book = app_values.app_info.book
        elements = book.get_page(self.page-1)
        content = [Factory.Space()] + [el.make_content() for el in elements]
        have = False
        comments = {}
        for el in elements:
            if el.have_note:
                have = True
                comments.update(el.notes)
        if have:
            content.append(Factory.NotesDelimeter())
            for note in comments:
                code : str = comments[note] 
                code = code.replace(']','').replace('[','').replace('&bl;', '').replace('&br;','')
                ind = note[1:]
                note_text = book.notes[ind] if ind in book.notes else 'This note don\'t found!'
                content.append(Factory.Note(text= f'{code} - {note_text}'))
        content.append(Factory.Space())
        return content

    def deselect(self):
        self.selection = False
        for child in self.ids.page_content.children:
            child.deselect()