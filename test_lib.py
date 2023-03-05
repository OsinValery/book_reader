

from kivy.app import runTouchApp
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout


class MyWidget(Screen):
    def do_action(self, wid):
        print('press')
        print(wid)
        print(wid.parent)
        wid.parent.canvas.before.clear()
        with wid.parent.canvas.before:
            Color(1,0,0,1)
            pos = wid.parent.pos
            Rectangle(size = wid.parent.size, pos = pos)

    def __init__(self, **kw):
        super().__init__(**kw)
        grid = GridLayout(cols = 2, size = self.size)
        self.add_widget(grid)
        for i in range(4):
            wid = AnchorLayout(size_hint = [1,1], anchor_x = 'left', anchor_y = 'bottom')
            wid.add_widget(Button(
                text = str(i), 
                on_press = self.do_action, 
                size= [100,50],
                pos = wid.pos,
                size_hint = [None, None]
            ))
            grid.add_widget(wid)


runTouchApp(MyWidget(), )


            



