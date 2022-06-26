
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


app = ReaderApp()
app.run()