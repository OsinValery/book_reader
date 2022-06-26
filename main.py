
# 2 lines for pyinstaller
import sys
import os
import shutil
os.environ['KIVY_NO_FILELOG'] = '1'
os.environ["KIVY_NO_CONSOLELOG"] = "1"
from kivy.config import Config
Config.set('kivy', 'log_enable', '0')
# for pyinstaller
from kivy.resources import resource_add_path
from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS["error"])


from kivymd.app import MDApp
from kivy.core.window import Window

from reader import PageScreen
import app_values


class ReaderApp(MDApp):
    def build(self):
        Window.clearcolor = (1,1,1,1)
        app_values.app_info.book.content.append([])
        self.load_all_kv_files(os.path.join(self.directory, 'kvfiles'))
        return PageScreen(size = Window.size)

    def read_book(self):
        filename = 'avidreaders.ru__prestuplenie-i-nakazanie-dr-izd.fb2'
        file = os.path.join(self.directory, 'assets', filename)
        new_file = os.path.join(self.user_data_dir, filename)
        if not os.path.exists(new_file):
            shutil.copyfile(file, new_file)
        app_values.app_info.book.read(new_file,app_values.app_info.max_elements_per_page)


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    app = ReaderApp()
    app.run()