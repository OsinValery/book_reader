

from kivy.app import runTouchApp
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout


class MyWidget(Screen):
    def do_action(self, wid, arg = ...):
        print(wid)
        print(arg)

    def __init__(self, **kw):
        super().__init__(**kw)
        text = '[ref=2]Hello[ref=1]World[/ref][/ref]'
        lab = Label(text = text, markup = True, size_hint = [None, None])
        lab.size = lab.texture_size
        lab.pos = [400,200]
        lab.text_size = (600, None)
        with lab.canvas.before:
            Color(1,0,1,0.2)
            Rectangle(size = lab.size, pos = lab.pos)
        lab.bind(on_ref_press = self.do_action)
        self.add_widget(lab)


runTouchApp(MyWidget(), )


            



