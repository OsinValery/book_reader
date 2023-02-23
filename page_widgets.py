import os

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, BooleanProperty, \
    StringProperty, ObjectProperty, NumericProperty, DictProperty
from kivy.graphics import Color, Rectangle
from kivy.factory import Factory
from kivy.core.window import Window

import app_values

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

    @property
    def page_widget(self):
        """returns Page widget or None"""
        widget = self
        while widget.parent != None:
            if type(widget) == Factory.Page:
                return widget
            widget = widget.parent
        return None


class Space(Widget, PageContent):
    pass

# base class for all active elements of page
class SelectableLabel(Label, PageContent):
    selections = ListProperty([])
    selection_figures = ListProperty([])
    first_pos = ListProperty([0,0])
    selection = BooleanProperty(False)

    referization = ListProperty([])
    choosenWord = StringProperty('')

    @property
    def root_screen(self):
        """returns screen named 'reader' or None"""
        widget = self
        while widget.parent != None:
            if 'name' in dir(widget.parent) and widget.parent.name == 'reader':
                return widget.parent
            widget = widget.parent
        return None

    def on_refference(self, inst, data=...):
        self.choosenWord = data

    def on_touch_up(self, touch):
        if self.choosenWord != '' and app_values.app_info.translate_text:
            choosenWord = self.referization[int(self.choosenWord)]
            root = self.root_screen
            if root:
                root.present(choosenWord)
            else:
                print('can\'t present content in SelectableLabel.on_refference')
            self.choosenWord = ''
        # clear value
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
        if not app_values.app_info.select_text:
            return
        shapes = []
        words = []
        pos = [pos[0], pos[1]]
        pos[0] -= 40

        if self.parent:
            if type(self.parent == SelectablePair):
                if self == self.parent.children[0] and len(self.parent.children) > 1:
                    pos[0] -= (self.parent.width * self.parent.pad + self.parent.spacing)
                    pos[0] += 40
        

        direction = 'down'
        if pos[1] > self.first_pos[1] + 10:
            direction = 'up'
        elif (pos[0] < self.first_pos[0]) and (pos[1] > self.first_pos[1] - 10):
            direction = 'up'


        for element in self.refs:
            new_selections = []
            element_selected = False

            for points in self.refs[element]:
                x1, y1, x2, y2 = points
                y1 = self.pos[1] + self.height - y1
                y2 = self.pos[1] + self.height - y2
                rect = Rectangle(pos = [self.pos[0]+x1, y2],size=[x2-x1,abs(y2-y1)])
                new_selections.append(rect)  
                if element_selected:
                    continue
                
                if x1 < pos[0] and x2 >= pos[0] and y1 > pos[1] and y2 < pos[1]:
                    element_selected = True
                elif x1 < self.first_pos[0] and x2 >= self.first_pos[0] and \
                            y1 > self.first_pos[1] and y2 < self.first_pos[1]:
                        element_selected = True

                elif direction == 'up':
                    if y1 < self.first_pos[1]:
                        continue
                    if y2 < self.first_pos[1] and x2 > self.first_pos[0]:
                        continue
                    if y2 > pos[1] or (y1 > pos[1] and x1 < pos[0]):
                        continue
                    element_selected = True
                else:
                    if y2 > self.first_pos[1]:
                        continue
                    if x2 < self.first_pos[0] and y1 > self.first_pos[1]:
                        continue
                    if y1 < pos[1] or (x1 > pos[0] and pos[1] > y2):
                        continue
                    element_selected = True

            if element_selected:
                words.append(element)
                for rect in new_selections:
                    shapes.append(rect)
        
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


class PresentableLabel(SelectableLabel):
    # for graphics
    cite = BooleanProperty(False)
    poem = BooleanProperty(False)
    note = BooleanProperty(False)
    epigraph = BooleanProperty(False)
    another_properties = DictProperty({})

    def get_font(self, name):
        folder = App.get_running_app().directory
        return os.path.join(folder, 'assets', 'fonts', name)

    def resolve_css_properties(self):
        for property_ in self.another_properties:
            value = clear_css_value(self.another_properties[property_])
            if value in ['inherit', 'initial', 'unset']:
                continue
            if property_ == 'font-family':
                try:
                    self.font_family = value
                except:
                    print('can\'t set font family')
            elif property_ == 'font-size':
                self.font_size = value
            elif property_ == 'text-align':
                if value in ['center', 'right', 'left', 'justify']:
                    self.halign = value
            elif property_ in ['margin-bottom', 'margin-top']:
                pass
            elif property_ in ['text-indent', 'margin', 'padding']:
                pass
            else:
                print('unknown css property:', property_, 'with value:', value)


class Paragraph(PresentableLabel):

    def resolve_state(self):
        if self.another_properties != {}:
            self.resolve_css_properties()
        else:
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


class Unknown(PresentableLabel):
    pass

class Mistake(PresentableLabel):
    pass

class ImageData(Widget, PageContent):
    texture = ObjectProperty()
    cover = BooleanProperty(False)
    another_properties=DictProperty({})

    def get_size(self, icon_size):
        if not self.cover:
            width = 0.8 * (Window.width - icon_size * 2)
            scale = width / self.texture.size[0]
            return [width, scale * self.texture.size[1]]
        else:
            size = App.get_running_app().root.ids.page_presenter.ids.page.size
            return size[0] - 2 * icon_size, size[1]


class Title(PresentableLabel):
    def resolve_state(self):
        if self.another_properties != {}:
            self.resolve_css_properties()
        else:
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

class Note(PresentableLabel):
    pass

class SubTitle(PresentableLabel):
    def resolve_state(self):
        if self.another_properties != {}:
            self.resolve_css_properties()
        else:
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

class Stanza_empty(Space):
    pass

class Author(PresentableLabel):
    def resolve_state(self):
        if self.another_properties != {}:
            self.resolve_css_properties()
        elif self.epigraph:
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
class Text(PresentableLabel):
    def resolve_state(self):
        if self.another_properties != {}:
            self.resolve_css_properties()
        else:
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

class Poem_line(PresentableLabel):
    def resolve_state(self):
        if self.another_properties != {}:
            self.resolve_css_properties()
        else:
            if self.epigraph:
                self.size_hint_x = None
                self.font_name = self.get_font('NotoSans-Thin.ttf')
            else:
                if self.cite:
                    self.italic = True
                    self.font_name = self.get_font('NotoSans-MediumItalic.ttf')
                else:
                    self.font_name = self.get_font('NotoSans-Medium.ttf')

class Annotation_empty(Space):
    pass

class Title_Empty(Space):
    pass




def clear_css_value(value: str):
    if value == "": return ""
    return value.split()[0]

def get_in_percents(value):
    try:
        value = value.replace('%', '')
        return float(value) / 100
    except:
        return None
