import os
from .xml_tag import Xml_Tag
from typing import List
from bookframe import BookFrame
from .css_descriptor import CssDescriptor


class Html_Tag(Xml_Tag):
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
        if (self.tag == "p"):
            text = self.cunstruct_text(styles)
            return [BookFrame(text, 'p', self.attr)]
        if self.tag == 'h1':
            text = self.cunstruct_text(styles)
            return [BookFrame(None, "title_empty", {}), BookFrame(text, 'title', self.attr), BookFrame(None, "title_empty", {})]
        if self.tag in ['h2', "h3", 'h4', 'h5', 'h6']:
            text = self.cunstruct_text(styles)
            attr = self.attr
            attr['lavel'] = self.tag
            return [BookFrame(None, "title_empty", {}), BookFrame(text, 'subtitle', self.attr), BookFrame(None, "title_empty", {})]

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







