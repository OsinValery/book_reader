from kivy.properties import ListProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.animation import Animation


class BottomSheet(Widget):
    background_color = ListProperty([0, 0, 0, 0.6])
    content_background = ListProperty([1,1,1,1])
    animation_duration = NumericProperty(0)
    opening_time = NumericProperty(0.1)

    radius = NumericProperty(10)
    '''radius of background rounded rectangle '''  

    padding = NumericProperty(30)  
    '''upper padding of widget'''


    def __init__(self, content,  **kwargs):
        super().__init__(**kwargs)
        self.size = [Window.width, content.height]

        self.ids.box.add_widget(content)
        content.pos_hint_y = None

        if 'content_background' in kwargs:
            self.content_background = kwargs['content_background']

    def resize(self, new_height = 100):
        d = self.animation_duration
        Animation(height = new_height, d=d).start(self)
        Animation(height=new_height,d=d).start(self.ids.box)

    def open(self):
        height = self.height
        self.height = 0
        self.ids.box.height = 0
        Window.add_widget(self)
        d = self.opening_time
        Animation(height=height,d=d).start(self)
        Animation(height=height,d=d).start(self.ids.box)        
    
    def dismiss(self):
        def dismiss(*args):
            Window.remove_widget(self)
        
        d = self.opening_time
        a = Animation(height=0, d=d)
        a.bind(on_complete=dismiss)
        a.start(self)
    
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            self.dismiss()
            return True
        super().on_touch_down(touch)
        return True
    
    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            return True
        super().on_touch_up(touch)
        return True

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return True
        super().on_touch_move(touch)
        return True