
import os
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.metrics import dp

from kivymd.uix.navigationdrawer.navigationdrawer import MDNavigationLayout
from kivymd.uix.toolbar.toolbar import MDTopAppBar
from kivymd.uix.menu.menu import MDDropdownMenu
from kivymd.uix.bottomsheet.bottomsheet import MDCustomBottomSheet
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget

from libretranslatepy import LibreTranslateAPI

import app_values
from page import Page

class PageScreen(MDNavigationLayout):
    word = StringProperty('click on the words in the text')
    translation_result = StringProperty('Here you may see translated text' )
    translater = ObjectProperty(LibreTranslateAPI("https://translate.argosopentech.com/"))

    def close_library(self):
        self.ids.page_screen.current = 'book'

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


class PagePresenter(Widget):
    cur_page = NumericProperty(1)

    @property
    def book(self):
        return app_values.app_info.book

    def init_page(self):
        self.page = Page(
            size = self.parent.size, 
            page = self.cur_page
        )
        self.add_widget(self.page)

    def back(self):
        self.seek(self.cur_page-1)

    def forward(self):
        self.seek(self.cur_page+1)

    def seek(self, number):
        self.cur_page = self.page.page = number
        content = self.page.ids.page_content
        content.clear_widgets()
        self.page.ids.page_scroll.scroll_y = 1
        if self.page.copping:
            self.page.copping = False
            self.page.remove_widget(self.page.bubble)
        self.page.selection = False
        for el in self.page.prepare():
            content.add_widget(el)

    def change_book(self):
        self.seek(1)
        self.ids.page_forward.disabled = self.book.length == 1


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


class LibraryPresenter(MDList):
    def update_library(self):
        self.clear_widgets()
        for book in app_values.app_info.library:
            line = OneLineAvatarIconListItem(
                on_press = self.choose_book,
                text = book
            )
            # x.parent.parent is link on "line"
            line.add_widget(IconLeftWidget(
                icon='book', 
                on_press=lambda x: self.choose_book(x.parent.parent))
            )
            self.add_widget(line)

    def choose_book(self, arg):
        app_values.app_info.book.read(
            os.path.join(app_values.app_info.book_dir, arg.text), 
            app_values.app_info.max_elements_per_page
        )
        root = self.root_screen
        root.ids.page_presenter.change_book()
        root.ids.page_screen.current = 'book'

    @property
    def root_screen(self):
        """returns screen named 'reader' or None"""
        widget = self
        while widget.parent != None:
            if 'name' in dir(widget.parent) and widget.parent.name == 'reader':
                return widget.parent
            widget = widget.parent
        return None