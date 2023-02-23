
from typing import Dict, Tuple
from .xml_tag import Xml_Tag


class XmlParser:

    @staticmethod 
    def determine_xml_encoding(file_path:str) -> str:
        with open(file_path, 'rb') as file:
            line = str(file.readline())
        enc_pos = line.find('encoding=') + 10
        enc_end = line.find('"', enc_pos)
        encoding = line[enc_pos:enc_end]
        return encoding

    @staticmethod
    def get_close_tag(name: str) -> str:
        return "</" + name + ">"

    @staticmethod
    def get_tag_arguments(tag:str) -> Tuple[str, Dict[str, str]]:
        attr = {}
        space_pos = tag.find(' ')
        if space_pos == -1:
            return tag, attr
        real_tag = tag[:space_pos]
        pos = space_pos + 1
        while pos < len(tag):
            eq_pos = tag.find('=',pos)
            if eq_pos == -1:
                pos = len(tag) + 10
            else:
                name = tag[pos:eq_pos].strip()
                val_start = tag.find('"',eq_pos)
                val_end = tag.find('"', val_start+1)
                value = tag[val_start+1:val_end]
                pos = val_end + 1
                attr[name] = value
        return real_tag, attr

    def is_self_closed(self, tag: str) -> bool:
        if tag == '': return False
        pos = -1
        while (tag[pos].isspace()) and (pos > -len(tag)):
            pos -= 1
        if pos == -len(tag): return False
        return tag[-1] == '/'

    def parce_string(self, string:str, pos:int) -> Tuple[Xml_Tag, int]:
        root = Xml_Tag()
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
        closed = False
        while (not closed) and (pos < len(string)):
            content_start = pos
            while (pos < len(string)) and string[pos] != "<":
                pos += 1
            if (pos >= len(string)): return root, pos
            plain_text = string[content_start:pos]
            if plain_text != '' and not plain_text.isspace():
                plain_tag = Xml_Tag()
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

    def parce_xml_file(self, full_path: str) -> Xml_Tag:
        try:
            encoding = self.determine_xml_encoding(full_path)
            with open(full_path, mode="r", encoding=encoding) as file:
                content = file.read()
                pos = content.find('>') + 1
                return self.parce_string(content, pos)[0]
        except Exception:
            return Xml_Tag()


            
            






