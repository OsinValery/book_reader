import os
import xml.etree.ElementTree as ElementTree
import fb2_book

class Book():
    def __init__(self) -> None:
        self.file_path = ''
        self.content = []
        self.notes = {}
        self.format = 'fb2'
    
    def read(self, filepath, max_elements_per_page=20):
        self.content = []
        self.notes = {}
        self.file_path = filepath
        self.format = os.path.split(self.file_path)[-1]
        self.format: str = self.format[-3:]
        self.max_elements_per_page = max_elements_per_page
        if self.format == 'fb2':
            self.read_fb2()
        else:
            raise Exception('unknown file format: '+ self.format)
        
    def read_fb2(self):
        content = ElementTree.parse(self.file_path)
        elements = []
        notes = {}
        assets = {}

        for child in content.getroot():
            elements.append(child)
        for element in elements:
            if element.attrib == {'name': 'notes'}:
                # text notes 
                for child in element:
                    if child.attrib != {}:
                        notes[child.attrib['id']] = ''
                        for el in child:
                            if el.text:
                                notes[child.attrib['id']] += el.text
            elif 'binary' in element.tag:
                # pictures
                child = element
                assets[child.attrib['id']] = {'type': child.attrib['content-type'], 'data': child.text}
            
            elif 'body' in element.tag:
                # main text (body)
                # realization downside
                pass
            else:
                pass
                # description of the book

        self.notes = notes
        # encoding = ??
        with open(self.file_path, 'rb') as file:
            line = str(file.readline())
        suffix = line[line.find('encoding="')+10:]
        encoding = suffix[:suffix.find('"')]
        with open(self.file_path, 'r', encoding=encoding) as file:
            content = file.read()
        body_pos = content.find('<body>')
        pos_close = content.find('</body>')
        body = content[body_pos: pos_close+7]
        book_body = fb2_book.fb2_parser(body, 0)[0]
        elements = book_body.work()
        # divide into pages
        page = []
        i = 0
        for el in elements:
            if el.type == 'image':
                name = el.content[1:]
                if name in assets:
                    el.content = assets[name]['data']
                    el.attributs = {'type':assets[name]['type']}
                else:
                    el.attributs['broken'] = 1
            page.append(el)
            i += 1
            if i == self.max_elements_per_page:
                self.content.append(page)
                i = 0
                page = []
        if page != []:
            self.content.append(page)
    
    @property
    def length(self):
        return len(self.content)
    
    def get_page(self, number):
        return self.content[number]

