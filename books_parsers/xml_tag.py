from .any_book_tag import AnyBookTag
from typing import List, Union


class Xml_Tag(AnyBookTag):
    def find_tag_in_tree(self, name: str) -> Union['Xml_Tag', None]:
        if self.tag == name:
            return self
        child: Xml_Tag = None
        for child in self.content:
            res = child.find_tag_in_tree(name)
            if res != None:
                return res
        return None

    def find_all_tags_in_tree(self, name:str) -> List['Xml_Tag']:
        if self.tag == name:
            return [self]
        result = []
        child: Xml_Tag = None
        for child in self.content:
            result += child.find_all_tags_in_tree(name)
        return result

    def get_text_if_only_plain_text(self) -> str:
        if len(self.content) == 1 and self.content[0].tag == 'plain_text':
            return self.content[0].text
        return ""

    def print(self, lavel = 0) -> str:
        infix = " " * (4 * lavel)
        result = infix + self.tag + ':'
        if self.tag == "plain_text":
            return result + "  " + self.text + '\n'
        else:
            result += "\n"
        for tag in self.content:
            result += tag.print(lavel + 1)
        if self.content == []:
            result += infix + '    ' + "empty_contnet\n"
        return result
