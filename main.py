
# 2 lines for pyinstaller
import sys
import os
import shutil
from threading import Thread

os.environ['KIVY_NO_FILELOG'] = '1'
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
from kivy.utils import platform

if platform not in ['android', 'ios']:
    from kivy.config import Config
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '700')
from kivy.lang.builder import Builder
# for pyinstaller
from kivy.resources import resource_add_path
# from kivy.logger import Logger, LOG_LEVELS
# Logger.setLevel(LOG_LEVELS["error"])


from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.clock import Clock

from book import Book
from reader import PageScreen
import app_values
from localizator import get_lang

class ReaderApp(MDApp):
    def load_all_kv_files(self, path_to_directory: str) -> None:
        for path_to_dir, _ , files in os.walk(path_to_directory):
            if (
                "venv" in path_to_dir
                or ".buildozer" in path_to_dir
                or os.path.join("kivymd") in path_to_dir
            ):
                continue
            for name_file in files:
                if (
                    os.path.splitext(name_file)[1] == ".kv"
                    and name_file != "style.kv"  # if use PyInstaller
                    and "__MACOS" not in path_to_dir  # if use Mac OS
                ):
                    path_to_kv_file = os.path.join(path_to_dir, name_file)
                    Builder.load_file(path_to_kv_file)

    def build(self):
        Window.clearcolor = (1,1,1,1)
        if not app_values.app_info.read_settings():
            app_values.app_info.interface_language = get_lang()
            app_values.app_info.write_settings()
        self.set_theme(app_values.app_info.theme)
        self.load_all_kv_files(os.path.join(self.directory, 'kvfiles'))

        asset_dir = os.path.join(self.directory, 'assets')
        booksdir = self.books_dir
        app_values.app_info.book_dir = booksdir

        if not os.path.exists(booksdir):
            os.makedirs(booksdir)
        for filename in os.listdir(asset_dir):
            if filename[-4:] == '.fb2':
                if not os.path.exists(os.path.join(booksdir, filename)):
                    shutil.copyfile(
                        os.path.join(asset_dir, filename), 
                        os.path.join(booksdir, filename)
                    )
        for file in os.listdir(booksdir):
            app_values.app_info.library.append(file)

        self.read_book()

        return PageScreen(size = Window.size)

    def read_book(self):
        filename = 'about.fb2'
        file = os.path.join(self.user_data_dir,'books', filename)
        app_values.app_info.book = Book()
        app_values.app_info.book.read(file,app_values.app_info.max_elements_per_page)

    def on_start(self):
        super().on_start()

        def read_last_book():
            last_book = app_values.app_info.get_last_page()
            if last_book:
                # != None
                app_values.app_info.book.read(
                    os.path.join(app_values.app_info.book_dir, last_book[0]), 
                    app_values.app_info.max_elements_per_page
                )
            def after(dt=0):
                self.root.ids.page_presenter.change_book()
                self.root.ids.page_presenter.seek(last_book[1])
            # can't influe on graphics from another thread - 
            # this is old bag!!!!!
            # Clock does function in main thread
            Clock.schedule_once(after)
        thread = Thread(target = read_last_book, daemon=True)
        thread.start()

    @property
    def books_dir(self):
        return os.path.join(self.user_data_dir, 'books')
    
    def set_theme(self, theme):
        if theme in ['Dark', 'Light']:
            self.theme_cls.theme_style = theme
            if theme == 'Light':
                self.theme_cls.primary_hue = '500'
                self.theme_cls.primary_palette = 'Blue'
            else:
                self.theme_cls.primary_hue = '500'
                self.theme_cls.primary_palette = 'Gray'
            app_values.app_info.set_theme(theme)
        else:
            print('ReaderApp.set_theme:')
            print('unknown theme style: ', theme)
            print('Must be "Dark" or "Light" !!!!')
        


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    app = ReaderApp()
    app.run()