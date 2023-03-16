import os
from .xml_tag import Xml_Tag
from typing import List, Dict
from page_elements.html_bookframe import HtmlBookFrame
from .css_descriptor import CssDescriptor
from .css_measurement_systems import *

style_tags = ['i', 'em', 'strong', 'b', 'sub', 'sup', 'a']
char = chr(8203)
numeric_properties = [
    'font-size', 'border-spacing', 'letter-spacing', 'line-height',
    'pitch-range', 'pitch', 'richness', 'text-indent', 'word-spacing'
]
string_properties = [
    'color', 'border-collapse', 'caption-side', 'direction', 
    'list-style-image', 'list-style-position', 'list-style-type',
    'list-style', 'qotes', 'text-align', 'visibility', 'text-transform'
]
'orphans', 'widows'

class Html_Entity_with_preprocessor(Xml_Tag):
    def __init__(self) -> None:
        super().__init__()
        self.css = {}
        self.own_css = {}
        self.inherited_properties = {}

    def preprocessing(self, rootpath: str, styles: CssDescriptor):
        self.prepare_for_css_properties(None)
        self.find_css_properties(styles, [self])
        self.tree_shake(rootpath)

    def decrease_font_size_for_subtree(self):
        self.css['font-size'] = decrease_font_size_by_value(self.css['font-size'], 4)
        for child in self.content:
            child.decrease_font_size_for_subtree()

    def prepare_for_css_properties(self, parent:Xml_Tag = None):
        if self.tag in default_css_properties:
            self.css.update(default_css_properties[self.tag])
        elif parent:
            self.css = deepcopy(parent.css)
        else:
            print('unpredictable situation with tag', self.tag, 'with parent', parent.tag)

        if 'style' in self.attr:
            small_descriptor = CssDescriptor()
            small_descriptor.update_from_string(self.tag + ' {' + self.attr['style'] + '}')
            self.own_css = small_descriptor.content[self.tag]
        
        for child in self.content:
            child.prepare_for_css_properties(self)

    def grab_properties_from_style(self, styles: CssDescriptor, stack: List['Html_Tag'] = []) -> Dict[str, str]:
        css = {}
        if self.tag in styles.content:
            css.update(styles.content[self.tag])
        if 'class' in self.attr:
            class_ = self.attr['class']
            subclasses: str = class_.split()
            for subclass in subclasses:
                if self.tag + "." + subclass in styles.content:
                    css.update(styles.content[self.tag + "." + subclass])
                elif "." + subclass in styles.content:
                    css.update(styles.content["." + subclass])
        return css

    def find_css_properties(self, styles: CssDescriptor, stack: List['Html_Tag'] = []):
        style_css = self.grab_properties_from_style(styles, stack)
        # from self.attr['style']
        style_css.update(self.own_css)
        parent: 'Html_Tag' = None
        if len(stack) != 0:
            parent = stack[-1]
        
        for inherited_css_property in self.inherited_properties:
            if not inherited_css_property in style_css:
                if inherited_css_property in (numeric_properties + string_properties):
                    self.css[inherited_css_property] = self.inherited_properties[inherited_css_property]
                else:
                    print(
                        'tryes inherit unknown css property', 
                        inherited_css_property,
                        'with value:',
                        self.inherited_properties[inherited_css_property]
                    )

        for css_property in style_css:
            parent_value = None
            default_value = None
            if css_property in self.css:
                default_value = self.css[css_property]

            if css_property in self.inherited_properties:
                parent_value = self.inherited_properties[css_property]
            elif parent:
                if css_property in parent.css:
                    parent_value = parent.css[css_property]
                else:
                    parent_value = default_value
            else:
                parent_value = default_value
            
            if css_property in numeric_properties:
                if default_value == None:  default_value = '0dp'
                if parent_value == None:   parent_value = '0dp'
                new_value = work_measurement_systems_for_inheritance(
                    value = style_css[css_property],
                    parent_value = parent_value,
                    default_value = default_value
                )
                self.css['font-size'] = new_value
                self.inherited_properties[css_property] = new_value
            elif css_property in string_properties:
                self.css[css_property] = style_css[css_property]
                self.inherited_properties[css_property] = style_css[css_property]
            else:
                # non - inheritable
                if not css_property in self.css:
                    continue
                    print('unknown css property for class: ' + self.tag + ' key:' + css_property, 
                      'with value:', 
                      style_css[css_property]
                    )
                self.css[css_property] = style_css[css_property]

        for css_property in self.inherited_properties:
            value = self.inherited_properties[css_property]
            self.share_property_with_children(css_property, value)

        for child in self.content:
            child.find_css_properties(styles, stack + [self])

    def share_property_with_children(self, property_: str, value):
        for child in self.content:
            child.inherit_property_from_parent(property_, value)

    def inherit_property_from_parent(self, proprty_:str, value):
        if (proprty_ in numeric_properties) or (proprty_ in string_properties):
            self.inherited_properties[proprty_] = value

    def tree_shake(self, rootpath: str) -> List['Html_Entity_with_preprocessor']:
        if self.tag == 'body':
            new_children = []
            for child in self.content:
                new_children += child.tree_shake(rootpath)
            self.content = new_children
            return self.content
        
        if self.tag == 'small':
            replacemant_array = []
            for child in self.content:
                child.decrease_font_size_for_subtree()
                replacemant_array += child.tree_shake(rootpath)
            return replacemant_array
        
        if self.tag == 'img':
            if 'src' in self.attr:
                full_path = os.path.join(rootpath, self.attr['src'])
                self.attr['path'] = full_path

        elif self.tag == 'image':
            if 'xlink:href' in self.attr:
                full_path = os.path.join(rootpath, self.attr['xlink:href'])
                self.attr['path'] = full_path
                if 'height' in self.attr:
                    self.attr['another']['height'] = self.attr['height']
                if 'width' in self.attr:
                    self.attr['another']['width'] = self.attr['width']

        if self.tag == 'plain_text':
            self.text = char + '[size=' + str(self.css['font-size']) + ']' + char + self.text + char + '[/size]' + char
        
        if (self.tag == 'a' and self.content == [] ):
            link = Html_Tag()
            link.attr = self.attr
            link.tag = 'link'
            return [link]

        if self.tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'] + style_tags:
            def apply_tag(ch: 'Html_Entity_with_preprocessor'):
                tag = self.tag
                if tag == 'p':
                    return
                elif tag == 'a':
                    print('unpredictable content inside a!!!!')
                elif tag in ['i', 'em']:
                    ch.make_cursive_subtree()
                else:
                    ch.make_bold_subtree()
            
            my_children = []
            unexpected_found = False
            output_list = [self]
            for child in self.content:
                subtree = child.tree_shake(rootpath)
                for entity in subtree:
                    if not unexpected_found:
                        if entity.tag in (['br', 'plain_text'] + style_tags):
                            my_children.append(entity)
                        elif entity.tag == 'link':
                            output_list.append(entity)
                        else:
                            unexpected_found = True
                            output_list.append(entity)
                            apply_tag(entity)
                    else:
                        output_list.append(entity)
                        apply_tag(entity)
            self.content = my_children
            return output_list

        new_children = []
        for child in self.content:
            new_children += child.tree_shake(rootpath)
        self.content = new_children
        return [self]

    def make_bold_subtree(self):
        self.css['font-weight'] = 'bold'
        for child in self.content:
            child.make_bold_subtree()

    def make_cursive_subtree(self):
        self.css['font-style'] = 'italic'
        for child in self.content:
            child.make_cursive_subtree()


class Html_Tag(Html_Entity_with_preprocessor):
    def wrap_text_with_tag(self, text: str, tag: str, attr = None):
        if tag in ['h1', 'h2', "h3", 'h4', 'h5', 'h6', 'p']:
            return text
        if tag == 'i' or tag == 'em':
            return '[i]' + char + text + char + '[/i]' + char
        elif tag == 'b':
            return '[b]' + char + text + char + '[/b]' + char
        elif tag == 'strong':
            return '[b]' + char + text + char + '[/b]' + char
        elif tag in ['sub','sup']:
            return '[' + tag + ']' + char + text + char + '[/' + tag + ']' + char
        elif tag == 'a':
            link = 'empty'
            if 'href' in attr:
                link = attr['href']
            else:
                print(attr)
            return char + '[color=#FF0000]' + char + f'<a src={link}>' + text + '</a>' + char + '[/color]' + char
        else:
            print('unknown tag to wrap!')
            print(tag)
            return text

    def processing(self) -> List[HtmlBookFrame]:
        # I garantee, that tree is correct here
        result = []

        if self.tag in ['p', 'h1', 'h2', "h3", 'h4', 'h5', 'h6'] + style_tags:
            text = ''
            for child in self.content:
                if child.tag == 'plain_text':
                    text += child.text
                elif child.tag == 'br':
                    text += '\n'
                elif child.tag in style_tags:
                    new_children = child.processing()
                    for new_child in new_children:
                        if new_child.type == 'html_text':
                            text += new_child.content
                        else:
                            print(f'unexpexted tag in processing for "{self.tag}": child_tag: ', new_child.type, '(first)')
                else:
                    print(f'unexpexted tag in processing for "{self.tag}": child_tag: ', child.tag)
            if  text != '':
                text = self.wrap_text_with_tag(text, self.tag, self.attr)
                choose_tag = self.tag
                if self.tag == 'p':
                    choose_tag = 'html_p'
                elif self.tag in style_tags:
                    choose_tag = 'html_text'
                result.append(HtmlBookFrame(text, choose_tag, self.attr))
            return result

        elif self.tag == 'img':
            if 'src' in self.attr:
                return [HtmlBookFrame(None, "file_image", self.attr)]
            elif 'alt' in self.attr:
                return [HtmlBookFrame(self.attr['alt'],'subtitle', {})]
            else:
                return [HtmlBookFrame("broken image",'subtitle', {})]

        elif self.tag == 'image':
            if 'xlink:href' in self.attr:
                if 'height' in self.attr:
                    self.attr['another']['height'] = self.attr['height']
                if 'width' in self.attr:
                    self.attr['another']['width'] = self.attr['width']
                return [HtmlBookFrame(None, "file_image", self.attr)]
            else:
                return [HtmlBookFrame("broken image",'subtitle', {})]

        elif self.tag == 'script' or self.tag == 'br':
            return []
        
        elif self.tag == 'plain_text':
            return [HtmlBookFrame(self.text, 'text', self.attr)]
    
        elif self.tag == 'link':
            return [HtmlBookFrame(None, 'link', self.attr)]

        elif self.tag == 'blockquote':
            print('remake blockquote')
            children = []
            for el in self.content:
                new_children = el.processing()
                for new_child in new_children:
                    new_child.add_attribute('cite', True)
                    children.append(new_child)
            return children

        elif self.tag in ['body', 'div', "section", 'span', 'svg']:
            result = []
            child: Html_Tag = None
            for child in self.content:
                result += child.processing()
            return result
        
        elif self.tag == 'li':
            content = []
            child: Html_Tag = None
            for child in self.content:
                content += child.processing()
            return [HtmlBookFrame(content, 'li', self.attr)]
    
        elif self.tag == 'hr':
            result = [HtmlBookFrame('None', 'divider', self.attr)]
            child: Html_Tag = None
            for child in self.content:
                result += child.processing()
            return result

        """print('unknown tag: ', self.tag)
        print('content:')
        print(self.attr)
        print(self.text)
        print(self.content)"""
        return [HtmlBookFrame(self.text, self.tag, self.attr)]


    def work(self, styles = CssDescriptor(), root_path = "") -> List[HtmlBookFrame]:
        self.preprocessing(root_path, styles)
        self.attr['another'] = self.css
        self.check_links(root_path)
        print(self.print())
        return self.processing()
    
    def check_links(self, rootpath):
        self.attr['links_targets'] = []
        if 'id' in self.attr:
            self.attr['links_targets'].append(self.attr['id'])
        if 'name' in self.attr:
            self.attr['links_targets'].append(self.attr['name'])
        if 'href' in self.attr:
            if '://' in self.attr['href']:
                # external src
                self.attr['href'] = 'empty'
        for child in self.content:
            child.check_links(rootpath)
            self.attr['links_targets'] += child.attr['links_targets']







