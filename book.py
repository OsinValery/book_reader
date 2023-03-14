import os
import shutil
import zipfile

from kivy.app import App
import chardet
from typing import List, Dict
from page_elements.bookframe import BookFrame

from books_parsers.any_book_tag import AnyBookTag
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
        print('book', self.file_path, 'was opened')

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
        content = book_parser.get_book_content(entries[0])
        self.content = content[0]
        self.notes = content[1]

    def read_html(self):
        print(self.file_path)
        book = html_book.HtmlBook()
        self.content, comments = book.get_book_content(self.file_path)

    def read_fb2(self):
        parser = fb2_book.FB2Book()
        elements = []
        assets = {}
        fb2_tag = parser.parce_xml_file(self.file_path)

        # find description
        description_data = fb2_tag.find_tag_in_tree('description')
        description = fb2_book_description.FB2_Book_Deskription()
        if description_data:
            description.parse(description_data.text)

        # get content
        bodies = fb2_tag.find_all_tags_in_tree('body')
        if len(bodies) > 0:
            book_body = bodies[0]
            elements = book_body.work()

            # read notes
            for body_tag in bodies[1:]:
                if 'name' in body_tag.attr and body_tag.attr['name'] == 'notes':
                    for child in body_tag.content:
                        if child.tag == 'section':
                            if 'id' in child.attr:
                                s_id = child.attr['id']
                                self.notes[s_id] = child
                                child.add_attribute('note', True)

        # read binaries
        binaries = fb2_tag.find_all_tags_in_tree('binary')
        for binary in binaries:
            attributs = binary.attr
            assets[attributs['id']] = {'type': attributs['content-type'], 'data': binary.text}
        
        # get result: book content

        def work_book_element(el, page):
            if el.type == 'image':
                if 'l:href' in el.attributs:
                    name = el.attributs['l:href']
                elif 'xlink:href' in el.attributs:
                    name = el.attributs['xlink:href']
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


    @property
    def length(self):
        return len(self.content)
    
    def get_page(self, number) -> List[BookFrame]:
        return self.content[number]

    def get_page_by_link(self, link) -> int:
        if link in self.notes:
            return self.notes[link]
        return -1

