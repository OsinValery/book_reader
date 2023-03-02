from typing import Dict, List
import os
from kivy.core.text import LabelBase

class CssDescriptor:
    def __init__(self) -> None:
        self.content: Dict[str, Dict[str, str]] = {}
        self.new_fonts = {}
    
    def update(self, class_:str, key: str, value: str):
        class_ = class_.lower()
        if class_ not in self.content:
            self.content[class_] = {}
        self.content[class_][key] = value
    
    def register_new_font(self, root_path: str):
        for font_family in self.new_fonts:
            try:
                fn_bold = None
                fn_italic = None
                fn_regular = None
                fn_both = None
                for entity in self.new_fonts[font_family]:
                    full_path = os.path.join(root_path, entity['path'])
                    if not os.path.exists:
                        continue
                    if entity['bold'] and entity['italic']:
                        fn_both = full_path
                    elif entity['bold']:
                        fn_bold = full_path
                    elif entity['italic']:
                        fn_italic = full_path
                    else:
                        fn_regular = full_path
                    LabelBase.register(font_family, fn_regular, fn_italic, fn_bold, fn_bolditalic=fn_both)
            except:
                pass

    def resolve_new_font(self, css):
        print('add new font family')
        print(css)
        font_family = ""
        is_bold = False
        is_italic = False
        font_path = ""
        for pair in css.split(';'):
            options = pair.split(':')
            if len(options) == 2:
                key, value = options
                key = key.strip()
                value = value.strip()
                if key == 'font-family':
                    font_family = value
                elif key == 'font-style':
                    if value == 'italic':
                        is_italic = True
                elif key == 'font-weight':
                    if value == 'bold':
                        is_bold = True
                elif key == 'src':
                    if 'url' in value:
                        font_path = value.replace('url', '').replace(')', '').replace('(','').strip()
        if font_family not in self.new_fonts:
            self.new_fonts[font_family] = []
        self.new_fonts[font_family].append({'bold': is_bold, 'italic': is_italic, "path": font_path})

    def update_from_file(self, file_path: str):
        with open(file_path, mode = 'r') as file:
            content = file.read()
            self.update_from_string(content)
    
    def update_from_string(self, string: str):
        current_tags:List[str]  = []
        pos = 0
        # TODO учесть возможность комментариев
        while True:
            opening_brase_pos = string.find("{", pos)
            if opening_brase_pos == -1:
                break
            classes = string[pos:opening_brase_pos].split(',')
            current_tags = [cl.strip() for cl in classes]
            closing_brase_pos = string.find('}', opening_brase_pos)
            if closing_brase_pos == -1:
                closing_brase_pos = len(string)
            classes_content = string[opening_brase_pos+1:closing_brase_pos]
            if len(current_tags) == 1 and current_tags[0] == '@font-face':
                self.resolve_new_font(classes_content)
            else:
                for line in classes_content.split(';'):
                    parts = line.split(':')
                    if len(parts) == 2:
                        property_ = parts[0].strip()
                        value = parts[1].strip()
                        for cl in current_tags:
                            self.update(cl, property_, value)
            pos = closing_brase_pos + 1
        
    
    def update_from_descriptor(self, descriptor: 'CssDescriptor'):
        for cl in descriptor.content:
            for key in descriptor.content[cl]:
                self.update(cl, key, descriptor.content[cl][key])
        for font_family in descriptor.new_fonts:
            if font_family not in self.new_fonts:
                self.new_fonts[font_family] = []
            for font in self.new_fonts[font_family]:
                if not font in self.new_fonts[font_family]:
                    self.new_fonts[font_family].append(font)

            



