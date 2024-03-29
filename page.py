
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.clock import _default_time as time
from kivy.properties import NumericProperty, BooleanProperty
from kivy.core.clipboard import Clipboard

from kivymd.uix.snackbar.snackbar import Snackbar
from kivymd.uix.bottomsheet.bottomsheet import MDListBottomSheet

import app_values
from localizator import Get_text

class Page(Factory.Widget):
    page = NumericProperty(0)
    selection = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selectionAction = MDListBottomSheet()

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
        self.deselect()
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.selection:
            text = ''
            for child in self.ids.page_content.children:
                # boxlayout keeps his child widgets in reversed order
                text = child.get_selected_text() + text

            def cancel(arg=None):
                self.deselect()
                self.selectionAction.dismiss()

            def copy(arg=None):
                cancel()
                Clock.schedule_once(lambda dt: self.copy_text(text))

            def translate(arg=...):
                cancel()
                Clock.schedule_once(lambda dt: self.root_screen.present(text))
            
            def near(*args):
                self.deselect()
                return True

            if text != '':
                self.selectionAction = MDListBottomSheet()
                self.selectionAction.add_item(text=Get_text('info_copy'), icon = 'content-copy', callback=copy)
                self.selectionAction.add_item(text=Get_text('info_cancel'), icon = 'cancel', callback=cancel)
                self.selectionAction.add_item(text=Get_text('info_translate'), icon = 'book', callback=translate)  
                self.selectionAction.value_transparent = (0,0,0,0.5)
                self.selectionAction.on_dismiss = near
                self.selectionAction.open()      
            
        return super().on_touch_up(touch)
    
    def copy_text(self, text):
        Clipboard.copy(text)
        snack = Snackbar(
            text = Get_text('info_text_copied'),
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
        add_space = not elements[0].is_cover
        if add_space:
            yield Factory.Space()
        for el in elements:
            yield el.make_content()
        have = False
        comments = {}
        for el in elements:
            if el.have_note:
                have = True
                comments.update(el.notes)
        if have:
            yield Factory.NotesDelimeter()
            for note in comments:
                ind = note[1:]
                note_text = book.notes[ind] if ind in book.notes else Get_text('info_unknown_note')
                if type(note_text) == str:
                    code : str = comments[note] 
                    code = code.replace(']','').replace('[','').replace('&bl;', '').replace('&br;','')
                    yield Factory.Note(text= f'{code} - {note_text}')
                else:
                    note_elements = note_text.work()
                    for el in note_elements:
                        yield el.make_content()
        
        if add_space:
            yield Factory.Space()

    def deselect(self):
        self.selection = False
        for child in self.ids.page_content.children:
            child.deselect()
        
    def reset_task(self, content):
        limit = Clock.get_time() + 1/25
        finished = False
        while (time() < limit) and not finished:
            try:
                wid = self.widgets_generator.__next__()
                content.add_widget(wid)
            except:
                finished = True
        if not finished:
            Clock.schedule_once(lambda dt: self.reset_task(content), 0)


    def reset_content(self):
        self.deselect()
        content = self.ids.page_content
        content.clear_widgets()
        self.widgets_generator = self.prepare()
        self.ids.page_scroll.scroll_y = 1
        self.reset_task(content)
        """        for el in self.widgets_generator:
            content.add_widget(el)"""