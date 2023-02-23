
from .html_Tag import Html_Tag
from .xml_parser import XmlParser
from typing import Tuple

class Html_Parser(XmlParser):
    ignore_tags = ["style", 'strong']

    def parce_string(self, string:str, pos:int) -> Tuple[Html_Tag, int]:
        root = Html_Tag()
        if string[pos] != '<':
            pos = string.find("<", pos)
        close = string.find(">", pos)
        tag_txt = string[pos+1:close]
        self_closed = self.is_self_closed(tag_txt)
        # divide tag and xml arguments here!!
        root.tag, root.attr = self.get_tag_arguments(tag_txt)
        if self_closed:
            return root, close + 1
        pos = close + 1
        # ignore parsing content of tags with text content
        # this code only takes text with styles markup
        if root.tag in self.ignore_tags:
            close_tag_text = self.get_close_tag(root.tag)
            close_tag_pos = string.find(close_tag_text, pos)
            if close_tag_pos == -1:
                close_tag_pos = len(string)
            root.text = string[pos:close_tag_pos]
            return root, close_tag_pos + len(close_tag_text)
        closed = False
        while (not closed) and (pos < len(string)):
            content_start = pos
            while (pos < len(string)) and string[pos] != "<":
                pos += 1
            if (pos >= len(string)): return root, pos
            plain_text = string[content_start:pos]
            if plain_text != '' and not plain_text.isspace():
                plain_tag = Html_Tag()
                plain_tag.tag = "plain_text"
                plain_tag.text = plain_text
                root.append(plain_tag)
            # work '<'
            if pos + 1 == len(string):
                closed = True
            if string[pos+1] == '/':
                closed = True
                close_pos = string.find('>', pos+1)
                pos = close_pos + 1
            #it is internal tag
            if not closed:
                sub_tag, pos = self.parce_string(string, pos)
                root.append(sub_tag)
        return root, pos








