import os
import shutil
import zipfile

from kivy.app import App
import chardet
from typing import List, Dict
from bookframe import BookFrame

from books_parsers.any_book_tag import AnyBookTag
from books_parsers.xml_parser import XmlParser
import books_parsers.fb2_book as fb2_book
import books_parsers.fb2_book_description as fb2_book_description
import books_parsers.txt_book as txt_book
import books_parsers.epub_book as epub_book
import books_parsers.Html_book as html_book

class Book():
    def __init__(self) -> None:
        self.file_path = ''
        self.content: List[List[BookFrame]] = []
        self.notes: Dict[str, AnyBookTag] = {}
        self.format = 'fb2'
        self.max_elements_per_page = 10

    def read(self, filepath: str, max_elements_per_page=20):
        self.content = []
        self.notes = {}
        self.file_path = filepath
        self.format: str = os.path.split(self.file_path)[-1]
        print(self.format)
        self.max_elements_per_page = max_elements_per_page
        if self.format[-3:] == 'fb2':
            self.format = 'fb2'
            self.read_fb2()
        elif self.format[-3:] == 'txt':
            self.format = 'txt'
            self.read_txt()
        elif self.format[-4:] == "epub":
            file_folder = App.get_running_app().user_data_dir
            file_name = self.format
            self.format = "epub"
            self.read_epub(file_folder, file_name)
        elif self.format[-4:] == 'html':
            self.format = "html"
            self.read_html()
        else:
            raise Exception('unknown file format: '+ self.format)

    def read_fb2(self):
        elements = []
        assets = {}

        # encoding = ??
        encoding = XmlParser.determine_xml_encoding(self.file_path)

        # read content
        with open(self.file_path, 'r', encoding=encoding) as file:
            content = file.read()

        # read description        
        des_pos = content.find('<description')
        des_end = content.find('>', des_pos)
        des_fin = content.find('</description>')
        description_text = content[des_end+1:des_fin]
        description = fb2_book_description.FB2_Book_Deskription()
        description.parse(description_text)

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
        cover = description.get_cover()
        for el in cover:
            page = []
            work_book_element(el, page)
            self.content.append(page)
        
        f_cover = description.get_foreign_cover()
        for el in f_cover:
            page = []
            work_book_element(el, page)
            self.content.append(page)

        # present book description
        self.content.append(description.get_description())

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

    def read_txt(self):
        elements = []
        full_content = []
        encoding = 'utf-8'
        found_notes = False
        notes_lines: List[BookFrame] = []
        with open(self.file_path, mode="rb") as test_file:
            test_content = test_file.read()
            enc = chardet.detect(test_content)
        # here I have language of book, encoding and confidence of detection in !(enc)
        encoding = enc['encoding']
        with open(self.file_path, mode = "rt", encoding=encoding) as file:
            for line in file.readlines():
                text = line.strip()
                if text != "" and not text.isspace():
                    frame = BookFrame(text, "txt_p", {})
                    full_content.append(frame)
                    elements.append(frame)
                    if found_notes:
                        notes_lines.append(text)
                if text == 'notes':
                    found_notes = True
                elif len(elements) == self.max_elements_per_page:
                    self.content.append(elements)
                    elements = []
        if len(elements) != 0:
            self.content.append(elements)
        if found_notes:
            self.notes = txt_book.organise_notes(notes_lines)
            for frame in full_content:
                frame.add_list_of_notes(txt_book.detect_notes(frame.content, self.notes))
                frame.content = txt_book.underline_notes(frame.content)

    def read_epub(self, save_path, file_name: str):
        book_path = os.path.join(save_path, "temp_book")
        if (os.path.exists(book_path)):
            shutil.rmtree(book_path)
        os.makedirs(book_path)
        target_path = os.path.join(book_path, file_name.replace('.epub', '.zip'))
        final_path = os.path.join(book_path, "content")
        shutil.copy(self.file_path, target_path)
        with zipfile.ZipFile(target_path) as zf:
            zf.extractall(final_path)
        book_parser = epub_book.EpubBookParser(final_path)
        entries = book_parser.get_containers_paths()
        print(entries)
        content = book_parser.get_book_content(entries[0])
        self.content = content[0]
        self.notes = content[1]

    def read_html(self):
        print(self.file_path)
        book = html_book.HtmlBook()
        self.content, comments = book.get_book_content(self.file_path)

    @property
    def length(self):
        return len(self.content)
    
    def get_page(self, number) -> List[BookFrame]:
        return self.content[number]

