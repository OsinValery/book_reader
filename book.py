import os
import fb2_book
import fb2_book_description

class Book():
    def __init__(self) -> None:
        self.file_path = ''
        self.content = []
        self.notes = {}
        self.format = 'fb2'
        self.description = fb2_book_description.FB2_Book_Deskription()

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

        # read description        
        des_pos = content.find('<description')
        des_end = content.find('>', des_pos)
        des_fin = content.find('</description>')
        description_text = content[des_end+1:des_fin]
        self.description = fb2_book_description.FB2_Book_Deskription()
        self.description.parse(description_text)

        # read text
        body_pos = content.find('<body>', des_fin)
        pos_close = content.find('</body>', body_pos)
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


        # get result: book content

        def work_book_element(el, page):
            if el.type == 'image':
                if 'l:href' in el.attributs:
                    name = el.attributs['l:href']
                elif 'xlink:href' in el.attributs:
                    name = 'xlink:href'
                else:
                    print(el.attributs)
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

        # get cover
        cover = self.description.get_cover()
        if cover != []:
            page = []
            for el in cover:
                work_book_element(el, page)
            self.content.append(page)
        
        f_cover = self.description.get_foreign_cover()
        if f_cover != []:
            page = []
            for el in cover:
                work_book_element(el, page)
            self.content.append(page)

        # present book description
        self.content.append(self.description.get_description())

        # divide into pages
        page = []
        i = 0
        for el in elements:
            work_book_element(el, page)
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

