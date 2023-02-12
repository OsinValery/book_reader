
from typing import List, Dict
import bookframe
from localizator import Get_text

def organise_notes(notes:List[str]) -> Dict[str, 'Txt_tag']:
    result = {}
    note_container = None
    note_id = '0'
    notes_mass_len = len(notes)
    i = 0
    while not notes[i].isdigit() and i < notes_mass_len:
        i += 1

    if i == notes_mass_len:
        return result
    
    while i < len(notes) and i < notes_mass_len:
        text = notes[i]
        i += 1
        if text.isdigit():
            if note_container is not None:
                result[note_id] = note_container
            note_container = Txt_tag()
            note_container.set_tag("note")
            note_id = text
        else:
            tag = Txt_tag()
            tag.set_tag("note_line")
            tag.set_text(text)
            note_container.add_content(tag)

    if note_container is not None:
        result[note_id] = note_container
    return result

def detect_notes(text: str, all_notes) -> Dict[str, str]:
    result = {}

    pos = 0
    while pos != -1:
        pos = text.find('[', pos)
        if (pos != -1) and (pos + 1) < len(text):
            end_of_digit = text.find(' ', pos)
            if end_of_digit == -1:
                end_of_digit = len(text)
            digit = text[pos+1:end_of_digit]
            if digit.isdigit():
                content = Txt_tag()
                content.set_tag("note")
                child = Txt_tag()
                child.set_tag('note_line')
                child.set_text(Get_text("info_unknown_note"))
                content.add_content(child)
                if (digit in all_notes):
                    content = all_notes[digit]
                result[" " + digit] = content
            pos = text.find(']', end_of_digit)        

    return result

def underline_notes(text: str) -> str:
    pos = 0
    while pos != -1:
        pos = text.find('[', pos)
        if (pos != -1):
            end = text.find(']', pos)
            if end != -1:
                payload = text[pos+1:end]
                text = text[:pos] + '[u][color=#00a400] (' + payload + ") [/color][/u] " + text[end+1:]
                end += 35   # remove [] and add color markup
            pos = end

    return text
    frame.content = frame.content.replace("[", '[u][color=#0000ffff] (').replace("]", ") [/color][/u] ")

class Txt_tag:

    def __init__(self):
        self.attr = {}
        self.tag = ''
        self.text = ''
        self.content : List[Txt_tag] = []

    def add_attribute(self, name, value):
        self.attr[name] = value
    
    def set_tag(self, tag):
        self.tag = tag
    
    def set_text(self, text):
        self.text = text
    
    def add_content(self,cont):
        self.content.append(cont)
    
    
    def work(self) -> List[bookframe.BookFrame]:
        if self.tag == 'note':
            result = []
            for el in self.content:
                result += el.work()
            return result
        # note_line
        return [bookframe.BookFrame(self.text, "note", {})]