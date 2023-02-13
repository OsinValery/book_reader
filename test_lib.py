import deep_translator

text = "test"
t = deep_translator.GoogleTranslator()



print(t.translate(text, source = 'en', target = "ru"))



from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.core.window import Window
from kivy.properties import BooleanProperty, StringProperty

Builder.load_string('''
<StatefulLabel>:
    active: stored_state.active
    orientation: "horizontal"
    size_hint: 1,1

    CheckBox:
        id: stored_state
        active: root.active
        on_release: root.store_checkbox_state()
    Label:
        text: root.text
        text_size: self.size
        
        canvas.before:
            Color:
                rgba: (0, 0.517, 0.705, 1) 
            Rectangle:
                pos: self.pos
                size: self.size
    Label:
        id: generate_state
        text: root.generated_state_text
    
    Button:
        text: "remove"
        on_press:
            root.remove_self()

<RV>:
    viewclass: 'StatefulLabel'
    RecycleBoxLayout:
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
''')

class StatefulLabel(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty()
    generated_state_text = StringProperty()
    active = BooleanProperty()
    index = 0

    '''
    To change a viewclass' state as the data assigned to it changes,
    overload the refresh_view_attrs function (inherited from
    RecycleDataViewBehavior)
    '''
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        if data['text'] == '0':
            self.generated_state_text = "is zero"
        elif int(data['text']) % 2 == 1:
            self.generated_state_text = "is odd"
        else:
            self.generated_state_text = "is even"
        super(StatefulLabel, self).refresh_view_attrs(rv, index, data)

    '''
    To keep state changes in the viewclass with associated data,
    they can be explicitly stored in the RecycleView's data object
    '''
    def store_checkbox_state(self):
        rv = App.get_running_app().rv
        rv.data[self.index]['active'] = self.active
    
    def remove_self(self):
        print('remove')
        print(self.index)
        rv = App.get_running_app().rv
        rv.remove_at_index(self.index)

class RV(RecycleView, App):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.size = Window.size
        self.data = [{'text': str(x), 'active': False} for x in range(40)]
        App.get_running_app().rv = self
    
    def remove_at_index(self, ind):
        self.data.remove(self.data[ind])

    def build(self):
        return self

if __name__ == '__main__':
    RV().run()