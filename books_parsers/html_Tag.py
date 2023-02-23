import os
from .xml_tag import Xml_Tag
from typing import List
from bookframe import BookFrame
from .css_descriptor import CssDescriptor


class Html_Tag(Xml_Tag):
    def apply_style(self, styles: CssDescriptor):
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
        if 'style' in self.attr:
            small_descriptor = CssDescriptor()
            small_descriptor.update_from_string(self.tag + ' {' + self.attr['style'] + '}')
            css.update(small_descriptor.content[self.tag])
        self.attr['another'] = css

    def cunstruct_text(self, styles: CssDescriptor) -> str:
        text = ""
        for child in self.content:
            if child.tag == "plain_text":
                text += child.text
            elif child.tag == "strong":
                text += '[b]' + child.text + "[/b]"
            elif child.tag == 'p':
                text += child.cunstruct_text(styles)
            else:
                print("unknown element:", child.tag)
                print('in Html_Tag.cunstruct_text')
        return text

    def work(self, styles = CssDescriptor(), root_path = "") -> List[BookFrame]:
        self.apply_style(styles)
        if (self.tag == "p"):
            text = self.cunstruct_text(styles)
            return [BookFrame(text, 'html_p', self.attr)]
        if self.tag == 'h1':
            text = self.cunstruct_text(styles)
            return [BookFrame(text, 'title', self.attr)]
        if self.tag in ['h2', "h3", 'h4', 'h5', 'h6']:
            text = self.cunstruct_text(styles)
            attr = self.attr
            attr['lavel'] = self.tag
            return [BookFrame(text, 'subtitle', self.attr)]

        if self.tag == 'img':
            if 'src' in self.attr:
                full_path = os.path.join(root_path, self.attr['src'])
                self.attr['path'] = full_path
                return [BookFrame(None, "file_image", self.attr)]
            elif 'alt' in self.attr:
                return [BookFrame(self.attr['alt'],'subtitle', {})]
            else:
                return [BookFrame("broken image",'subtitle', {})]

        if self.tag in ['body', 'div', "section"]:
            result = []
            print("нужно передать свойства css потомкам")
            child: Html_Tag = None
            for child in self.content:
                result += child.work(styles, root_path)
            return result
        print('unknown tag: ', self.tag)
        print('content:')
        print(self.attr)
        print(self.text)
        print(self.content)
        return [BookFrame(self.text, self.tag, self.attr)]







