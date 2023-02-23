from typing import Dict, List


class CssDescriptor:
    def __init__(self) -> None:
        self.content: Dict[str, Dict[str, str]] = {}
    
    def update(self, class_:str, key: str, value: str):
        if class_ not in self.content:
            self.content[class_] = {}
        self.content[class_][key] = value

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
                return
            classes = string[pos:opening_brase_pos].split(',')
            current_tags = [cl.strip() for cl in classes]
            closing_brase_pos = string.find('}', opening_brase_pos)
            if closing_brase_pos == -1:
                closing_brase_pos = len(string)
            classes_content = string[opening_brase_pos+1:closing_brase_pos]
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

            



