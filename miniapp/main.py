# 2 lines for pyinstaller
import sys
import os
os.environ['KIVY_NO_FILELOG'] = '1'
os.environ["KIVY_NO_CONSOLELOG"] = "1"
from kivy.config import Config
Config.set('kivy', 'log_enable', '0')
# for pyinstaller
from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS["error"])


from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.label.label import MDLabel



class PageScreen(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = 'test successed'
        self.color = (0,0,0,1)


class ReaderApp(MDApp):
    def build(self):
        Window.clearcolor = (1,1,1,1)
        return PageScreen(size = Window.size)


if __name__ == '__main__':

    app = ReaderApp()
    app.run()