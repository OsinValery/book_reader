# 2 lines for pyinstaller
import sys
import os
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
from kivymd.uix.navigationdrawer.navigationdrawer import MDNavigationLayout
from kivymd.uix.toolbar.toolbar import MDTopAppBar



class PageScreen(MDNavigationLayout):
    pass

class MyAppBar(MDTopAppBar):
    def open_menu(self, arg=...):
        pass

class ReaderApp(MDApp):
    def build(self):
        Window.clearcolor = (1,1,1,1)
        self.load_all_kv_files(os.path.join(self.directory, 'kvfiles'))
        return PageScreen(size = Window.size)


if __name__ == '__main__':

    app = ReaderApp()
    app.run()