
import os
import shutil

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.metrics import dp
import kivy.app
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permission,check_permission, Permission

from kivymd.uix.navigationdrawer.navigationdrawer import MDNavigationLayout
from kivymd.uix.toolbar.toolbar import MDTopAppBar
from kivymd.uix.menu.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import BaseListItem
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.filemanager.filemanager import MDFileManager

from bottom_sheet import BottomSheet
from libretranslatepy import LibreTranslateAPI
import deep_translator
from localizator import Get_text

import app_values

class PageScreen(MDNavigationLayout):
    cur_translater = StringProperty('')
    # не переводит сейчас - 0
    translation_progress = [0,0]
    word = StringProperty(Get_text('info_click_text') )
    translation_result = StringProperty(Get_text('info_translated_text'))
    google_translation_result = StringProperty(Get_text('info_translated_text'))

    # argos
    translater = ObjectProperty(LibreTranslateAPI())
    supported_languages = sorted(['en','ar','zh','fr','de','hi','id','ga','it','ja','ko','pl','pt','ru','es','tr','vi',])
    from_lang = StringProperty('ru')
    to_lang = StringProperty('en')

    # google
    google_translator = ObjectProperty(deep_translator.GoogleTranslator())
    google_supported_languages = sorted(deep_translator.GoogleTranslator().get_supported_languages(as_dict=True).values())
    google_from_lang = StringProperty('en')
    google_to_lang = StringProperty('ru')

    def close_library(self):
        self.ids.page_screen.current = 'book'

    def present(self, word):
        self.check_translator()
        self.word = word
        try:
            print('start translation for word:\n', word)
            if self.cur_translater == 'argos':
                if self.translation_progress[0] == 1:
                    return
                self.translation_progress[0] = 1
                self.translation_result = self.translater.translate(self.word, self.from_lang, self.to_lang)
                self.translation_progress[0] = 0
            elif self.cur_translater == 'google':
                if self.translation_progress[1] == 1:
                    return
                self.translation_progress[1] = 1
                text = self.google_translator.translate(self.word, source=self.google_from_lang, target=self.google_to_lang)
                self.google_translation_result = text
                self.translation_progress[1] = 0
            else:
                print('unknown translater')
            self.ids.translater.set_state("open")
        except Exception as e:
            print(e)
            def cancel(data=...):
                dialog.dismiss()
            def retry(data=...):
                cancel()
                self.present(word)
            dialog = MDDialog(
                text = Get_text('error_network_connection'),
                buttons = [
                    MDFlatButton(text=Get_text('info_cancel'), on_press=cancel),
                    MDRaisedButton(text=Get_text('info_again'), on_press=retry)
                ]
            )
            dialog.open()

    def close_settings(self):
        self.ids.page_screen.current = 'book'
    
    def check_translator(self):
        if app_values.app_info.translator == '':
            app_values.app_info.set_translator('argos')
        if self.cur_translater == '':
            self.cur_translater = app_values.app_info.translator

    # from settings
    def set_translator(self, translator):
        app_values.app_info.set_translator(translator)
        self.cur_translater = translator

    def set_menu_translater(self, page):
        if page == self.cur_translater:
            return
        if page == 'argos':
            if self.cur_translater == 'google':
                if self.google_from_lang in self.supported_languages:
                    self.from_lang = self.google_from_lang
                if self.google_to_lang in self.supported_languages:
                    self.to_lang = self.google_to_lang
            else:
                print('set_menu_translator: add action!!!')
        elif page == 'google':
            if self.cur_translater == 'argos':
                if self.from_lang in self.google_supported_languages:
                    self.google_from_lang = self.from_lang
                if self.to_lang in self.google_supported_languages:
                    self.google_to_lang = self.to_lang
            else:
                print('set_menu_translator: unknown translator for google!!!!!')
        else:
            print('set_menu_translator: unknown page !!!!!')
        self.cur_translater = page
        self.present(self.word)

    def change_language(self, arg = ...):
        self.ids.pagePresenterAppBar.title = Get_text('info_reader')
        self.ids.menu_header.title = Get_text('info_reader')        
        self.ids.library_app_bar.title = Get_text('info_library')
        self.ids.settings_app_bar.title = Get_text('info_settings')
        self.ids.menu_settings.text = Get_text('info_settings')
        self.ids.language_label.text = Get_text('info_language')
        self.ids.translater_header.title = Get_text('info_translater')
        self.ids.menu_select_book.text = Get_text('info_select_book')
        self.ids.translate_to.text = Get_text('info_translate_to')
        self.ids.translate_from.text = Get_text('info_translate_from')
        self.ids.select_text.text = Get_text('info_select_text')
        self.ids.translation_text.text = Get_text('info_translate_text')
        self.ids.change_theme.text = Get_text('info_change_theme')
        self.ids.translator_chooser_label.text = Get_text('info_translater')
        self.ids.google_translate_from.text = Get_text('info_translate_from')
        self.ids.google_translate_to.text = Get_text('info_translate_to')
        theme = kivy.app.App.get_running_app().theme_cls.theme_style
        self.ids.theme_changer.text = Get_text('theme_' + theme)
        self.ids.pagePresenterAppBar.change_language()

    def on_drop_file(self, window, file_path: bytes, x, y):
        file_path = file_path.decode("utf-8")
        ext = file_path[file_path.rfind('.'):]
        if ext in app_values.app_info.supported_formats:
            self.ids.page_screen.current = 'library'
            self.ids.library_list.load_book(file_path)

class PagePresenter(Widget):
    cur_page = NumericProperty(1)

    @property
    def book(self):
        return app_values.app_info.book

    def back(self):
        self.seek(self.cur_page-1)
        app_values.app_info.remember_page(self.cur_page)

    def forward(self):
        self.seek(self.cur_page+1)
        app_values.app_info.remember_page(self.cur_page)

    def seek(self, number):
        page = self.ids.page
        self.cur_page = page.page = number
        page.reset_content()

    def change_book(self):
        self.seek(1)
        self.ids.page_forward.disabled = self.book.length == 1



class MyAppBar(MDTopAppBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        menu_items = [{ 
            "viewclass": "OneLineListItem", 
            "text": Get_text('info_book_start'), 
            "height": dp(40), 
            "on_release": self.to_book_start
            },{ 
            "viewclass": "OneLineListItem", 
            "text": Get_text('info_book_end'), 
            "height": dp(40), 
            "on_release": self.to_book_end
            },{ 
            "viewclass": "OneLineListItem", 
            "text": Get_text('info_turn'), 
            "height": dp(40), 
            "on_release": self.seek
            }]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=3)
    
    def change_language(self):
        menu_items = [{ 
            "viewclass": "OneLineListItem", 
            "text": Get_text('info_book_start'), 
            "height": dp(40), 
            "on_release": self.to_book_start
            },{ 
            "viewclass": "OneLineListItem", 
            "text": Get_text('info_book_end'), 
            "height": dp(40), 
            "on_release": self.to_book_end
            },{ 
            "viewclass": "OneLineListItem", 
            "text": Get_text('info_turn'), 
            "height": dp(40), 
            "on_release": self.seek
            }]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=3)

    def seek(self, *args):
        self.menu.dismiss()
        bottom_sheet = BottomSheet(
            content = PageTurnerSheet(
                maximum=self.page_turner.book.length, 
                on_select = lambda page: self.seek_to_page(page),
                current = self.page_turner.cur_page
            ),
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

    def resolve_size(self, expanded):
        """returns new height of content depending on system keyboard size"""
        if not expanded or platform not in ['android', 'ios']:
            return 0.25 * Window.height
        # if hasattr(Window, 'keyboard_height') and Window.keyboard_height != None:
        #     return 0.25 * Window.height + Window.keyboard_height
        return 0.5 * Window.height
        

class LibraryPresenter(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._file_manager = MDFileManager(
            exit_manager = self.cancel,
            select_path = self.load_book,
            preview=False,
            ext = app_values.app_info.supported_formats
        )
        self.manager_open = False

    def cancel(self, arg = ...):
        self.manager_open = False
        self._file_manager.close()

    def load_book(self, path):
        # adds book into the library from internal storage
        if self.manager_open:
            self.manager_open = False
            self._file_manager.close()
        folder_with_books: str = kivy.app.App.get_running_app().books_dir
        filename = path.split('/')[-1]
        if filename in app_values.app_info.library:
            def add():
                new_path = os.path.join(folder_with_books, filename)
                if os.path.exists(new_path):
                    os.remove(new_path)
                shutil.copyfile(path, new_path)
                self.update_library()
            def start(arg=...):
                show_alert_book_exists(filename, add)
            Clock.schedule_once(start, 0.1)
        else:
            app_values.app_info.library.append(filename)
            shutil.copyfile(path, os.path.join(folder_with_books, filename))
            self.update_library()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self._file_manager.back()
        return True

    def prepare_choosing_file(self, arg = ...):
        if platform != 'android':
            self.start_choose_file()
        else:
            if check_permission(Permission.READ_EXTERNAL_STORAGE):
                self.start_choose_file()
            else:
                # request permission
                def work_prepare(*args, **kwargs):
                    print(args, kwargs)
                    permissions, results = args

                    if results[0]:
                        Clock.schedule_once(self.start_choose_file)
                    else:
                        Clock.schedule_once(show_alert_no_permission)
                request_permission(Permission.READ_EXTERNAL_STORAGE, work_prepare)

    def start_choose_file(self, arg=...):
        if self.manager_open:
            return
        self.manager_open = True
        self._file_manager.show('/')

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
            line.add_widget(IconRightWidget(
                icon = 'delete',
                icon_color = [1,0,0,1],
                on_press=lambda x: self.remove_book(x.parent.parent.text)
            ))

            self.add_widget(line)
        self.add_widget(BaseListItem(height = 200))

    def choose_book(self, arg):
        app_values.app_info.book.read(
            os.path.join(app_values.app_info.book_dir, arg.text), 
            app_values.app_info.max_elements_per_page
        )
        root = self.root_screen
        root.ids.page_presenter.change_book()
        root.ids.page_screen.current = 'book'
    
    def remove_book(self, name):
        full_path = os.path.join(app_values.app_info.book_dir, name)
        app_values.app_info.library.remove(name)
        os.remove(full_path)
        self.update_library()

    @property
    def root_screen(self):
        """returns screen named 'reader' or None"""
        widget = self
        while widget.parent != None:
            if 'name' in dir(widget.parent) and widget.parent.name == 'reader':
                return widget.parent
            widget = widget.parent
        return None


def show_alert_no_permission():
    def close(data=...):
        popup.dismiss()
    
    popup = MDDialog(
        text = Get_text('error_no_permission'),
        title = Get_text('error_error'),
        radius = [8] * 4,
        buttons = [
            MDFlatButton(text = Get_text('info_ok'), on_press = close)
        ]
    )
    popup.open()

def show_alert_book_exists(name, callback):
    def cancel(arg=...):
        popups.dismiss()
    def akt(arg=...):
        popups.dismiss()
        callback()

    popups = MDDialog(
        text = Get_text('error_already_exists').format(name),
        title = Get_text('error_error'),
        radius = [8] * 4,
        buttons = [
            MDFlatButton(text = Get_text('info_ok'), on_press = akt),
            MDFlatButton(text = Get_text('info_no'), on_press = cancel),
        ]
    )
    popups.open()
