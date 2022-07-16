
# 2 lines for pyinstaller
import sys
import os
import shutil
os.environ['KIVY_NO_FILELOG'] = '1'
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
from kivy.utils import platform
from kivy.config import Config
Config.set('kivy', 'log_enable', '0')
if platform not in ['android', 'ios']:
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '700')
# for pyinstaller
from kivy.resources import resource_add_path
from kivy.logger import Logger, LOG_LEVELS
# Logger.setLevel(LOG_LEVELS["error"])


from kivymd.app import MDApp
from kivy.core.window import Window


from reader import PageScreen
import app_values
from localizator import get_lang

class ReaderApp(MDApp):
    def build(self):
        Window.clearcolor = (1,1,1,1)
        if not app_values.app_info.read_settings():
            app_values.app_info.interface_language = get_lang()
            app_values.app_info.write_settings()
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
        print(Window.size)
        return PageScreen(size = Window.size)

    def read_book(self):
        filename = 'about.fb2'
        file = os.path.join(self.user_data_dir,'books', filename)
        app_values.app_info.book.read(file,app_values.app_info.max_elements_per_page)
    
    @property
    def books_dir(self):
        return os.path.join(self.user_data_dir, 'books')


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    app = ReaderApp()
    app.run()