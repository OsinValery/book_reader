
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.properties import NumericProperty, ListProperty, \
    StringProperty, BooleanProperty, ObjectProperty
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock

from kivymd.uix.navigationdrawer.navigationdrawer import MDNavigationLayout
from kivymd.uix.toolbar.toolbar import MDTopAppBar
from kivymd.uix.menu.menu import MDDropdownMenu
from kivymd.uix.bottomsheet.bottomsheet import MDCustomBottomSheet
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton

from libretranslatepy import LibreTranslateAPI

import app_values
import page_widgets

class PageScreen(MDNavigationLayout):
    word = StringProperty('click on the words in the text')
    translation_result = StringProperty('Here you may see translated text' )
    translater = ObjectProperty(LibreTranslateAPI("https://translate.argosopentech.com/"))

    def present(self, word):
        self.word = word
        try:
            self.translation_result = self.translater.translate(self.word, 'ru', 'en')
            self.ids.translater.set_state("open")
        except:
            def cancel(data=...):
                dialog.dismiss()
            def retry(data=...):
                cancel()
                self.present(word)
            dialog = MDDialog(
                text = 'Network exception. Please, check internet connection and try again.',
                buttons = [
                    MDFlatButton(text='cancel', on_press=cancel),
                    MDRaisedButton(text='Again', on_press=retry)
                ]
            )
            dialog.open()


class Page(Widget):
    text = ListProperty()
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
        if self.copping:
            if not self.bubble.collide_point(*touch.pos):
                self.copping = False
                self.deselect()
                self.remove_widget(self.bubble)
                return True
        self.deselect()
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.copping:
            if not self.bubble.collide_point(*touch.pos):
                self.copping = False
                self.remove_widget(self.bubble)
                if self.selectation:
                    self.deselect()
                return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.root_screen.ids.page_presenter.ids.page_back.collide_point(*touch.pos):
            return False
        if self.root_screen.ids.page_presenter.ids.page_forward.collide_point(*touch.pos):
            return False

        if self.selectation:
            text = ''
            for child in self.ids.page_content.children:
                # boxlayout keeps his child widgets in reversed order
                text = child.get_selected_text() + text

            def cancel(arg=None):
                self.copping = False
                self.remove_widget(bubble)
                self.deselect()

            def copy(arg=None):
                self.copping = False
                self.remove_widget(bubble)
                self.deselect()
                Clock.schedule_once(lambda dt: self.copy_text(text))

            def translate(arg=...):
                self.copping = False
                self.remove_widget(bubble)
                self.deselect()
                Clock.schedule_once(lambda dt: self.root_screen.present(text))
                
            if not self.copping:
                bubble = Bubble(pos=touch.pos, background_color=(0,0,0,1), orientation='vertical')
                bubble.add_widget(BubbleButton(text='Копировать', on_press=copy))
                bubble.add_widget(BubbleButton(text='Отмена', on_press=cancel))
                bubble.add_widget(BubbleButton(text='Перевод', on_press=translate))
                bubble.pos[0] -= bubble.width/2
                if bubble.pos[0] < 5:
                    bubble.pos[0] = 5
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

    def prepare(self, elements):
        content = [el.make_content() for el in elements]
        have = False
        comments = {}
        for el in elements:
            if el.have_note:
                have = True
                comments.update(el.notes)
        if have:
            content.append(page_widgets.NotesDelimeter())
            book = app_values.app_info.book
            for note in comments:
                code : str = comments[note] 
                code = code.replace(']','').replace('[','').replace('&bl;', '').replace('&br;','')
                ind = note[1:]
                note_text = book.notes[ind] if ind in book.notes else 'This note don\'t found!'
                content.append(page_widgets.Note(text=code + ' - ' + note_text))
        return content

    def deselect(self):
        self.selectation = False
        for child in self.ids.page_content.children:
            child.deselect()


class PagePresenter(Widget):
    cur_page = NumericProperty(1)

    @property
    def book(self):
        return app_values.app_info.book

    def init_page(self):
        self.page_container = self
        # self.add_widget(self.page_container)
        self.page_container.add_widget(Page(
            size = self.parent.size, 
            text = self.book.get_page(self.cur_page-1),
            page = self.cur_page
        ))

    def back(self):
        self.seek(self.cur_page-1)

    def forward(self):
        self.seek(self.cur_page+1)

    def seek(self, number):
        for wid in self.page_container.children:
            if type(wid) == Page:
                self.page_container.remove_widget(wid)
                break
        self.cur_page = number
        new = Page(
            size = self.size,
            text = self.book.get_page(self.cur_page-1),
            page = self.cur_page 
        )
        self.page_container.add_widget(new)
        self.ids.page_forward.disabled = self.cur_page == self.book.length        


class MyAppBar(MDTopAppBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        menu_items = [{ 
            "viewclass": "OneLineListItem", 
            "text": "Начало книги", 
            "height": dp(40), 
            "on_release": self.to_book_start
            },{ 
            "viewclass": "OneLineListItem", 
            "text": "Конец книги", 
            "height": dp(40), 
            "on_release": self.to_book_end
            },{ 
            "viewclass": "OneLineListItem", 
            "text": "Пролистать", 
            "height": dp(40), 
            "on_release": self.seek
            }]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=3)
        
    def seek(self, *args):
        self.menu.dismiss()
        bottom_sheet = MDCustomBottomSheet(
            screen=PageTurnerSheet(
                maximum=self.page_turner.book.length, 
                on_select = lambda page: self.seek_to_page(page),
                current = self.page_turner.cur_page
            )
        )
        bottom_sheet.open()
    
    def to_book_start(self, *args):
        self.menu.dismiss()
        self.page_turner.seek(1)
    
    def to_book_end(self, *args):
        self.menu.dismiss()
        self.page_turner.seek(self.page_turner.book.length)

    def open_menu(self, button):
        self.menu.caller = button
        self.menu.open()

    def seek_to_page(self, number):
        self.page_turner.seek(number)


class PageTurnerSheet(BoxLayout):
    maximum =  NumericProperty(100)
    current = NumericProperty(0)

    def __init__(self, on_select, **kwargs):
        super().__init__(**kwargs)
        self.on_select = on_select

    def seek(self, page):
        self.on_select(page)

