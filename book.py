import os
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
        elements = []
        self.notes = {}
        assets = {}

        # encoding = ??
        with open(self.file_path, 'rb') as file:
            line = str(file.readline())
        enc_pos = line.find('encoding=') + 10
        enc_end = line.find('"', enc_pos)
        encoding = line[enc_pos:enc_end]

        # read content
        with open(self.file_path, 'r', encoding=encoding) as file:
            content = file.read()
        body_pos = content.find('<body>')
        pos_close = content.find('</body>')
        body = content[body_pos: pos_close+7]
        book_body = fb2_book.fb2_parser(body, 0)[0]
        elements = book_body.work()

        # read notes
        have_body = True
        while have_body:
            next_body = content.find('<body', pos_close + 7)
            if next_body == -1:
                have_body = False
            else:
                end_body = content.find('</body>', next_body)
                pos_close = content.find('>', next_body) + 1
                body_data = content[next_body:end_body+7]
                body_tag = fb2_book.fb2_parser(body_data)[0]
                if 'name' in body_tag.attr and body_tag.attr['name'] == 'notes':
                    for child in body_tag.content:
                        if child.tag == 'section':
                            if 'id' in child.attr:
                                s_id = child.attr['id']
                                self.notes[s_id] = child
                                child.add_attribute('note', True)

        # read bin data
        have_bin = True
        while have_bin:
            bin_pos = content.find('<binary', pos_close)
            if bin_pos == -1:
                have_bin = False
            else:
                start_content = content.find('>', bin_pos)
                end_bin = content.find('</binary>', start_content)
                tag = content[bin_pos+1:start_content]
                bin_content = content[start_content+1:end_bin]
                tag, attributs = fb2_book.get_tag_arguments(tag)
                assets[attributs['id']] = {'type': attributs['content-type'], 'data': bin_content}
                pos_close = end_bin + 9

        # divide into pages
        page = []
        i = 0
        for el in elements:
            if el.type == 'image':
                if 'l:href' in el.attributs:
                    name = el.attributs['l:href']
                else:
                    name = ''
                if name[0] == '#':
                    name = name[1:]
                    if name in assets:
                        el.content = assets[name]['data']
                        el.add_attribute('type', assets[name]['type'])
                    else:
                        el.add_attribute('broken', 1)
                else:
                    print('unknown image src: ' + name)
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

