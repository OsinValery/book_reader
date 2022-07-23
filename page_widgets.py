import os

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, BooleanProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.graphics import Color, Rectangle
from kivy.factory import Factory
from kivy.core.window import Window


#
# study kvfiles/page_widgets.kv
#

# wrapper for inactive types of content on the page
class PageContent:
    referization = ListProperty([])

    def deselect(self):
        return

    def select(self):
        return
    
    def get_selected_text(self):
        return ''


class Space(Widget, PageContent):
    pass

# base class for all active elements of page
class SelectableLabel(Label):
    selections = ListProperty([])
    selection_figures = ListProperty([])
    first_pos = ListProperty([0,0])
    selection = BooleanProperty(False)

    referization = ListProperty([])
    choosenWord = StringProperty('')

    # for graphics
    cite = BooleanProperty(False)
    poem = BooleanProperty(False)
    note = BooleanProperty(False)
    epigraph = BooleanProperty(False)

    @property
    def root_screen(self):
        """returns screen named 'reader' or None"""
        widget = self
        while widget.parent != None:
            if 'name' in dir(widget.parent) and widget.parent.name == 'reader':
                return widget.parent
            widget = widget.parent
        return None

    @property
    def page_widget(self):
        """returns Page widget or None"""
        widget = self
        while widget.parent != None:
            if type(widget) == Factory.Page:
                return widget
            widget = widget.parent
        return None

    def on_refference(self, inst, data=...):
        self.choosenWord = data

    def get_font(self, name):
        folder = App.get_running_app().directory
        return os.path.join(folder, 'assets', 'fonts', name)

    def on_touch_up(self, touch):
        if self.choosenWord != '':
            choosenWord = self.referization[int(self.choosenWord)]
            root = self.root_screen
            if root:
                root.present(choosenWord)
            else:
                print('can\'t present content in SelectableLabel.on_refference')
            self.choosenWord = ''
        self.first_pos = list(self.center)
        return super().on_touch_up(touch)
    
    def on_touch_down(self, touch):
        self.deselect()
        self.selection = True
        self.first_pos = list(touch.pos)
        if self.parent:
            if type(self.parent == SelectablePair):
                if self == self.parent.children[0] and len(self.parent.children) > 1:
                    self.first_pos[0] -= (self.parent.width * self.parent.pad + self.parent.spacing)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        self.choosenWord = ''
        if not self.selection:
            # event came from another widget
            self.selection = True
            if touch.pos[1] > self.center[1]:
                self.first_pos = [self.pos[0], self.height + self.pos[1]]
            else:
                self.first_pos = [self.pos[0] + self.width, self.pos[1]]        
            if self.parent:
                if type(self.parent == SelectablePair):
                    if self == self.parent.children[0] and len(self.parent.children) > 1:
                        self.first_pos[0] += (self.parent.width * self.parent.pad + self.parent.spacing)
        self.select(touch.pos)
        return super().on_touch_move(touch)

    def select(self, pos):
        shapes = []
        words = []
        pos = [pos[0], pos[1]]
        if self.parent:
            if type(self.parent == SelectablePair):
                if self == self.parent.children[0] and len(self.parent.children) > 1:
                    pos[0] -= (self.parent.width * self.parent.pad + self.parent.spacing)

        direction = 'down'
        if pos[1] > self.first_pos[1] + 10:
            direction = 'up'
        elif (pos[0] < self.first_pos[0]) and (pos[1] > self.first_pos[1] - 10):
            direction = 'up'

        if direction == 'up':
            for element in self.refs:
                points = self.refs[element][0]
                x1, y1, x2, y2 = points
                y1 = self.pos[1] + self.height - y1
                y2 = self.pos[1] + self.height - y2

                if x1 < pos[0] and x2 >= pos[0] and y1 > pos[1] and y2 < pos[1]:
                    rect = Rectangle(pos = [self.pos[0]+x1, y2],size=[x2-x1,abs(y2-y1)])
                    shapes.append(rect)
                    words.append(element)
                elif x1 < self.first_pos[0] and x2 >= self.first_pos[0] and \
                        y1 > self.first_pos[1] and y2 < self.first_pos[1]:
                    rect = Rectangle(pos = [self.pos[0]+x1,y2],size = [x2-x1,abs(y2-y1)])
                    shapes.append(rect)
                    words.append(element)
                else:
                    if y1 < self.first_pos[1]:
                        continue
                    if y2 < self.first_pos[1] and x2 > self.first_pos[0]:
                        continue
                    if y2 > pos[1] or (y1 > pos[1] and x1 < pos[0]):
                        continue

                    rect = Rectangle(pos = [self.pos[0]+x1,y2],size = [x2-x1,abs(y2-y1)])
                    shapes.append(rect)
                    words.append(element)
        else:
            for element in self.refs:
                points = self.refs[element][0]
                x1, y1, x2, y2 = points
                y1 = self.pos[1] + self.height - y1
                y2 = self.pos[1] + self.height - y2

                if x1 < pos[0] and x2 >= pos[0] and y1 > pos[1] and y2 < pos[1]:
                    rect = Rectangle(pos = [self.pos[0]+x1,y2],size = [x2-x1,abs(y2-y1)])
                    shapes.append(rect)
                    words.append(element)
                elif x1 < self.first_pos[0] and x2 >= self.first_pos[0] and \
                        y1 > self.first_pos[1] and y2 < self.first_pos[1]:
                    rect = Rectangle(pos = [self.pos[0]+x1,y2],size = [x2-x1,abs(y2-y1)])
                    shapes.append(rect)
                    words.append(element)
                else:
                    if y2 > self.first_pos[1]:
                        continue
                    if x2 < self.first_pos[0] and y1 > self.first_pos[1]:
                        continue
                    if y1 < pos[1] or (x1 > pos[0] and pos[1] > y2):
                        continue

                    rect = Rectangle(pos = [self.pos[0]+x1,y2],size = [x2-x1,abs(y2-y1)])
                    shapes.append(rect)
                    words.append(element)
        
        self.page_widget.selection = True
        self.selections = words

        for el in self.selection_figures:
            self.canvas.remove(el)
        with self.canvas:
            Color(*self.selection_color)
        self.selection_figures = shapes
        for el in shapes:
            self.canvas.add(el)

    def get_selected_text(self):
        result = ''
        indexes = [int(i) for i in self.selections]
        for word in sorted(indexes):
            result += self.referization[word] + ' '
        if result != '':
            result += '\n'
        return result.replace('&amp;','&').replace('&br;', ']').replace('&bl;','[')

    def deselect(self):
        for figure in self.selection_figures:
            self.canvas.remove(figure)
        self.selection = False
        self.selection_figures = []


class SelectablePair(BoxLayout):
    child = ObjectProperty(Widget())
    pad = NumericProperty(0.4)

    def deselect(self):
        for child in self.children:
            child.deselect()
    
    def select(self):
        pass

    def get_selected_text(self):
        text = ''
        for child in self.children:
            text += child.get_selected_text()
        return text


class Paragraph(SelectableLabel):

    def resolve_state(self):
        if self.cite: 
            self.font_size = 30
        self.halign = 'left'

        if not self.epigraph:
            if self.cite:
                self.font_name = self.get_font('NotoSans-ExtraLightItalic.ttf')
        else:
            self.halign = 'right'
            self.size_hint_x = None
            if self.cite:
                self.font_name = self.get_font('NotoSans-ThinItalic.ttf')
            else:
                self.font_name = self.get_font('NotoSans-Thin.ttf')


class Unknown(SelectableLabel):
    pass

class Mistake(SelectableLabel):
    pass

class ImageData(Widget, PageContent):
    texture = ObjectProperty()

    def get_size(self, icon_size):
        width = 0.7 * (Window.width - icon_size * 2)
        scale = width / self.texture.size[0]
        return [width, scale * self.texture.size[1]]


class Title(SelectableLabel):
    
    def resolve_state(self):
        if self.cite: 
            self.font_size = 38
        
        if self.cite and self.poem:
            self.font_name = self.get_font('NotoSans-ExtraBoldItalic.ttf')
        elif self.cite:
            self.font_name = self.get_font('NotoSans-SemiBoldItalic.ttf')
        elif self.poem:
            self.font_name = self.get_font('NotoSans-ExtraBold.ttf')
        else:
            pass


class NotesDelimeter(Widget,PageContent):
    pass

class Note(SelectableLabel):
    pass

class SubTitle(SelectableLabel):
    def resolve_state(self):
        if self.cite:
            self.font_name = self.get_font('NotoSans-ThinItalic.ttf')
        else:
            self.font_name = self.get_font('NotoSans-Italic.ttf')
  
        if self.epigraph:
            self.font_size = 28
            self.size_hint_x = None
        else:
            if self.cite:
                self.font_size = 30

class Stanza_empty(Widget, PageContent):
    pass

class Author(SelectableLabel):
    def resolve_state(self):
        if self.epigraph:
            self.font_size = 28
            self.size_hint_x = None
            if self.cite:
                self.font_name = self.get_font('NotoSans-ThinItalic.ttf')
            else:
                self.font_name = self.get_font('NotoSans-Light.ttf')
        else:
            self.font_name = self.get_font('NotoSans-Italic.ttf')
            if self.cite:
                self.font_size = 30


# this class != Paragraph
class Text(SelectableLabel):
    def resolve_state(self):
        if self.cite: 
            self.font_size = 30

        if not self.epigraph:
            if self.cite:
                self.font_name = self.get_font('NotoSans-ExtraLightItalic.ttf')
            else:
                self.font_name = self.get_font('NotoSans-Medium.ttf')
        else:
            self.size_hint_x = None
            if self.cite:
                self.font_name = self.get_font('NotoSans-ThinItalic.ttf')
            else:
                self.font_name = self.get_font('NotoSans-Thin.ttf')

class Poem_line(SelectableLabel):
    def resolve_state(self):
        if self.epigraph:
            self.size_hint_x = None
            self.font_name = self.get_font('NotoSans-Thin.ttf')
        else:
            if self.cite:
                self.italic = True
                self.font_name = self.get_font('NotoSans-MediumItalic.ttf')
            else:
                self.font_name = self.get_font('NotoSans-Medium.ttf')

