
from typing import List
from fb2_book import get_tag_arguments, fb2_parser
from bookframe import BookFrame
from localizator import Get_text

def resolve_space(text:str):
    if text == '' or text.isspace():
        text = Get_text('des_unknown')
    return text

class Person():
    def __init__(self):
        self.name = ''
        self.surname = ''
        self.patronimic = ''    
        self.emails = []
        self.nickname = ''
        # Pages in the internet
        self.cites = []
        self.id = ''
    
    def parse(self, text):
        pos = 0
        while pos < len(text):
            tag_start = text.find('<', pos)
            if tag_start == -1:
                pos = len(text) + 2
            else:
                tag_end = text.find('>', tag_start)
                tag_text = text[tag_start+1: tag_end]
                if tag_text[-1] == '/':
                    pos = tag_end + 1
                    continue
                info_end = text.find('</', tag_start+1)
                close_end = text.find('>', info_end)
                pos = close_end + 1
                information = text[tag_end+1:info_end]
                if tag_text == 'first-name':
                    self.name = information
                elif tag_text == 'last-name':
                    self.surname = information
                elif tag_text == 'middle-name':
                    self.patronimic = information
                elif tag_text == 'email':
                    self.emails.append(information)
                elif tag_text == 'id':
                    self.id = information
                elif tag_text == 'nickname':
                    self.nickname = information
                elif tag_text == 'home-page':
                    self.cites.append(information)
                else:
                    print(f'unknown info about person: {tag_text} \n content: {information}')
                    print(text)

    def describe(self) -> str:
        text = ''
        if self.name == '' and self.surname == '' and self.patronimic == '' and\
            self.emails == [] and self.nickname == '' and self.cites == [] and self.id == '':
            return Get_text('des_empty_person')
        text = ' - ' + Get_text('des_fio')
        fio = f'{self.surname} {self.name} {self.patronimic}'
        if fio.isspace():
            text += Get_text('des_unknown')
        else:
            text += fio
        if self.nickname != '' and not self.nickname.isspace():
            text += '\n - ' + Get_text('des_nick') + self.nickname
        if self.emails != []:
            text += '\n - email: ' + ', '.join(self.emails)
        if self.id != '' and not self.id.isspace():
            text += '\n - id: ' + self.id
        if self.cites != []:
            text += '\n - ' + Get_text('des_cites')
            text += ' \n'.join(self.cites)
        text += '\n'
        return text


class Date():
    def __init__(self) -> None:
        self.value = ''
        self.text = ''
    
    def parse(self, text:str, tag:str):
        real_tag, attr = get_tag_arguments(tag)
        if 'value' in attr:
            self.value = attr['value']
        self.text = text.strip()
    
    def present(self)-> str:
        if self.text != '' and not self.text.isspace():
            text = self.text
            if self.value != '' and not self.value.isspace():
                text = f'{text} ({self.value})'
        elif self.value != '' and not self.value.isspace():
            text = self.value
        else:
            text = Get_text('des_unknown')
        return text


class Title_Info():
    def __init__(self) -> None:
        self.ganres = []
        self.authors = []
        self.translators = []
        self.sequence = []
        self.name = ''
        self.key_words = ''
        self.annotation = None
        self.date = Date()
        # FB2_Tag
        self.image = None
        self.lang = 'unknown'
        self.src_lang = 'unknown'
    
    def parse(self, text:str):
        pos = 0
        while pos < len(text):
            start_tag = text.find('<', pos)
            if start_tag == -1:
                pos = len(text) + 10
            else:
                end_tag = text.find('>', start_tag)
                tag_content = text[start_tag+1:end_tag]
                if 'sequence' in tag_content:
                    real_tag, attr = get_tag_arguments(tag_content)
                    self.sequence.append(attr)
                    pos = end_tag + 1
                else:
                    if not 'date' in tag_content:
                        close_tag_text = '</' + tag_content + '>'
                    else:
                        close_tag_text = '</date>'
                    close = text.find(close_tag_text,end_tag)
                    if close == -1:
                        pos = end_tag + 1
                        print('no close tag for:', tag_content)
                        print('!'*20)
                        print(text)
                        continue
                    pos = close + len(close_tag_text)
                    content = text[end_tag+1:close]
                    if tag_content == 'genre':
                        self.ganres.append(content)
                    elif tag_content == 'author':
                        person = Person()
                        person.parse(content)
                        self.authors.append(person)
                    elif tag_content == 'book-title':
                        self.name = content
                    elif tag_content == 'annotation':
                        ann_text = text[start_tag:pos]
                        self.annotation = fb2_parser(ann_text)[0]
                    elif tag_content == 'coverpage':
                        self.image = fb2_parser(text[start_tag:pos])[0]
                    elif 'date' in tag_content:
                        self.date = Date()
                        self.date.parse(content, tag_content)
                    elif 'src-lang' in tag_content:
                        self.src_lang = content                
                    elif 'lang' in tag_content:
                        self.lang = content
                    elif tag_content == 'keywords':
                        self.key_words = content
                    elif tag_content == 'translator':
                        person = Person()
                        person.parse(content)
                        self.translators.append(person)
                    else:
                        print('unknown tag in title-info', tag_content)
                        print(content)

    def get_cover(self):
        if self.image == None:
            return []
        return self.image.work()
    
    def get_description(self) -> List[BookFrame]:
        result = []
        text = Get_text('des_name')
        if self.name == '':
            text += Get_text('des_unknown')
        else:
            text += self.name
        result.append(BookFrame(text, 'text', {}))
        if len(self.authors) == 0:
            text = Get_text('des_author') + Get_text('des_unknown')
            result.append(BookFrame(text, 'text', {}))        
        else:
            if len(self.authors) >= 2:
                text = Get_text('des_authors')
            else:
                text = Get_text('des_author')
            result.append(BookFrame(text, 'text', {}))
            for person in self.authors:
                text = person.describe()
                result.append(BookFrame(text, 'text', {}))
        text = Get_text('des_date') + self.date.present()
        result.append(BookFrame(text, 'text', {}))
        text = Get_text('des_lang') + resolve_space(self.lang)
        result.append(BookFrame(text, 'text', {}))
        if type(self) == Title_Info:
            text = Get_text('des_src-lang') + resolve_space(self.src_lang)
            result.append(BookFrame(text, 'text', {}))
        text = Get_text('des_ganres')
        if self.ganres == []:
            text += Get_text('des_unknown')
        else:
            text += ', '.join(self.ganres)
        result.append(BookFrame(text, 'text', {}))
        text = Get_text('des_seq')
        if self.sequence == []:
            text += Get_text('des_unknown')
        else:
            if len(self.sequence) > 1: text += '\n'
            for seq in self.sequence:
                cicle = ''
                if 'name' in seq:
                    cicle += seq['name']
                if 'number' in seq:
                    cicle += ' (' +  Get_text('des_part') + seq['number'] + ')'
                text += cicle + '\n'
        result.append(BookFrame(text, 'text', {}))

        if not self.annotation:
            result.append(BookFrame(Get_text('des_annotation') + Get_text('des_unknown'), 'text', {}))
        else:
            result.append(BookFrame(Get_text('des_annotation'), 'text', {}))
            result += self.annotation.work()
        text = Get_text('des_keywords') + resolve_space(self.key_words)
        result.append(BookFrame(text, 'text', {}))
        if len(self.translators) == 0:
            text = Get_text('des_translator') + Get_text('des_unknown')
            result.append(BookFrame(text, 'text', {}))
        else:
            des = 'translator' if len(self.translators) == 1 else 'translators'
            result.append(BookFrame(Get_text(f'des_{des}'), 'text', {}))
            for person in self.translators:
                result.append(BookFrame(person.describe(), 'text', {}))
        return result


class Document_Info():
    def __init__(self) -> None:
        self.document_authors = []
        self.publishers = []
        self.program_used = ''
        self.program_used_id = ''
        self.document_date = Date()
        self.src_url = ''
        self.src_scanner_person = ''
        self.id = ''
        self.version = ''
        # Fb2_Tag
        self.history = None   

    def parse(self, text:str):
        pos = 0
        while pos < len(text):
            start_tag = text.find('<', pos)
            if start_tag == -1:
                pos = len(text) + 10
            else:
                end_tag = text.find('>', start_tag)
                tag_content = text[start_tag+1:end_tag]
                if not 'date' in tag_content:
                    close_tag_text = '</' + tag_content + '>'
                else:
                    close_tag_text = '</date>'
                close_tag = text.find(close_tag_text, end_tag)
                if close_tag == -1:
                    pos = end_tag + 1
                    print('no close tag for:', tag_content)
                    print('!'*20)
                    print(text)
                    continue
                content = text[end_tag+1:close_tag]
                pos = close_tag + len(close_tag_text)
                if tag_content == 'author':
                    person = Person()
                    person.parse(content)
                    self.document_authors.append(person)
                elif tag_content == 'publisher':
                    person = Person()
                    person.parse(content)
                    self.publishers.append(person)
                elif tag_content == 'program-used':
                    self.program_used = content
                elif tag_content == 'program-id':
                    self.program_used_id = content
                elif tag_content == 'src-url':
                    self.src_url = content
                elif tag_content == 'src-ocr':
                    self.src_scanner_person = content
                elif tag_content == 'id':
                    self.id = content
                elif 'date' in tag_content:
                    self.document_date = Date()
                    self.document_date.parse(content, tag_content)
                elif tag_content == 'version':
                    self.version = content
                elif tag_content == 'history':
                    self.history = fb2_parser(text[start_tag:pos])[0]
                else:
                    print('unknown tag in document-info:', tag_content)
                    print(content)

    def get_description(self) -> List[BookFrame]:
        texts = [
            Get_text('des_program') + resolve_space(self.program_used),
            Get_text('des_program_id') + resolve_space(self.program_used_id),
            Get_text('des_time') + resolve_space(self.document_date.present()),
            Get_text('des_scanner') + resolve_space(self.src_scanner_person),
        ]
        if len(self.document_authors) == 0:
            texts += [Get_text('des_doc_authors') + Get_text('des_unknown')]
        else:
            text = Get_text('des_doc_authors') + '\n'
            for person in self.document_authors:
                text += person.describe() 
                text+= '\n'
            texts.append(text)

        texts.append(Get_text('des_source') + resolve_space(self.src_url))

        if len(self.publishers) == 0:
            texts += [Get_text('des_owner') + Get_text('des_unknown')]
        else:
            des = 'owner' if len(self.publishers) == 1 else 'owners'
            text = Get_text('des_' + des) + '\n'
            for person in self.publishers:
                text += person.describe() + '\n'
            texts.append(text)
        
        texts += ['id: ' + resolve_space(self.id)]
        texts.append(Get_text('des_version') + resolve_space(self.version))
        text = Get_text('des_history')
        if self.history is None:
            text += Get_text('des_unknown')
        texts.append(text)

        result = []
        for text in texts:
            result.append(BookFrame(text, 'text', {}))

        if self.history is not None:
            result += self.history.work()

        return result

class Publish_info():
    def __init__(self) -> None:
        self.book_name = ''
        self.publisher = ''
        self.publication_city = ''
        self.publication_time = ''    
        # have in sceme
        self.sequences = []
        self.isbn = ''

    def parse(self, text:str):
        pos = 0
        while pos < len(text):
            start_tag = text.find('<', pos)
            if start_tag == -1:
                pos = len(text) + 10
            else:
                end_tag = text.find('>', start_tag)
                tag_content = text[start_tag+1:end_tag]
                if 'sequence' in tag_content:
                    _, attr = get_tag_arguments(tag_content)
                    self.sequences.append(attr)
                    pos = end_tag + 1
                else:
                    # others have close tag
                    close_tag_text = '</' + tag_content + '>'
                    close_tag = text.find(close_tag_text, end_tag)
                    if close_tag == -1:
                        pos = end_tag + 1
                        print('no close tag for:', tag_content)
                        print('!'*20)
                        print(text)
                        continue
                    content = text[end_tag+1:close_tag]
                    pos = close_tag + len(close_tag_text)
                    if tag_content == 'book-name':
                        self.book_name = content
                    elif tag_content == 'publisher':
                        self.publisher = content
                    elif tag_content == 'city':
                        self.publication_city = content
                    elif tag_content == 'year':
                        self.publication_time = content
                    elif tag_content == 'isbn':
                        self.isbn = content
                    else:
                        print('unknown data in publish-info: ', tag_content)

    def get_description(self) -> List[BookFrame]:
        texts = [
            Get_text('des_name') + resolve_space(self.book_name),
            Get_text('des_publisher') + resolve_space(self.publisher),
            Get_text('des_city') + resolve_space(self.publication_city),
            Get_text('des_time') + resolve_space(self.publication_time),
        ]
        text = Get_text('des_seq')
        if self.sequences == []:
            text += Get_text('des_unknown')
        else:
            text += '\n'
        for seq in self.sequences:
            cicle = ''
            if 'name' in seq:
                cicle += seq['name']
            if 'number' in seq:
                cicle += ' (' +  Get_text('des_part') + seq['number'] + ')'
            text += cicle + '\n'
        texts.append(text)
        texts.append('isbn: ' + resolve_space(self.isbn))
        result = []
        for text in texts:
            result.append(BookFrame(text, 'text', {}))

        return result


class Original_Info(Title_Info):
    def __init__(self) -> None:
        super().__init__()
        self.lang = 'unknown'
        self.src_lang = 'unknown'
    def get_description(self) -> List[BookFrame]:
        result = super().get_description()
        result.append(BookFrame(Get_text('des_original_note'), 'p', {}))
        return result


class FB2_Book_Deskription():
    def __init__(self) -> None:
        self.title_info = Title_Info()
        self.document_info = Document_Info()
        self.publish_info = Publish_info()
        self.original_info = Original_Info()
        self.custom_info = ''
        self.custom_info_type = ''

    def parse(self, text):
        pos = 0
        while pos < len(text):
            tag_start = text.find('<', pos)
            if tag_start == -1:
                pos = len(text) + 10
            else:
                tag_end = text.find('>', tag_start)
                tag_text = text[tag_start+1:tag_end]
                if tag_text == 'title-info':
                    self.title_info = Title_Info()
                    close_tag = text.find('</title-info>',tag_end)
                    pos = close_tag + 13
                    content = text[tag_end+1:close_tag]
                    self.title_info.parse(content)
                elif tag_text == 'document-info':
                    self.document_info = Document_Info()
                    close_tag = text.find('</document-info>',tag_end)
                    pos = close_tag + 16
                    content = text[tag_end+1:close_tag]
                    self.document_info.parse(content)
                elif tag_text == 'publish-info':
                    self.publish_info = Publish_info()
                    close_tag = text.find('</publish-info>',tag_end)
                    pos = close_tag + 15
                    content = text[tag_end+1:close_tag]
                    self.publish_info.parse(content)
                elif tag_text == 'src-title-info':
                    self.original_info = Original_Info()
                    close_tag = text.find('</src-title-info>',tag_end)
                    pos = close_tag + 17
                    content = text[tag_end+1:close_tag]
                    self.original_info.parse(content)            
                elif tag_text == 'output':
                    close_tag = text.find('</output>', tag_end)
                    pos = close_tag + 10
                    print('found output tag in fb2 document. It must contain instruction for distributor. Likely, illegal access to document')
                elif 'custom-info' in tag_text:
                    real_tag, attr =  get_tag_arguments(tag_text)
                    if 'into-type' in attr:
                        self.custom_info_type = attr['into-type']
                    close_tag = text.find('</custom-info>',tag_end)
                    pos = close_tag + len('</custom-info>')
                    self.custom_info = text[tag_end+1:close_tag]
                else:
                    if tag_text[-1] == '/':
                        pos = tag_end + 1
                        continue
                    print('unknown tag: ', tag_text)
                    real, attr = get_tag_arguments(tag_text)
                    close = '</' + real + '>'
                    if close_tag == -1:
                        pos = tag_end + 1
                    else:
                        close_tag = text.find(close, tag_end)
                        pos = close_tag + len(close)

    def get_cover(self):
        return self.title_info.get_cover()

    def get_foreign_cover(self):
        return self.original_info.get_cover()
    
    def get_description(self) -> List[BookFrame]:
        result = [
            BookFrame(Get_text('des_description'), 'title', {}),
            BookFrame(None, 'empty', {})
        ]
        result += self.title_info.get_description()
        result.append(BookFrame(Get_text('des_foreign'), 'title', {}))
        result += self.original_info.get_description()
        result.append(BookFrame(Get_text('des_publication'),'title', {}))
        result += self.publish_info.get_description()
        if self.custom_info != '':
            result.append(BookFrame(Get_text('des_custom'),'title', {}))
            text = Get_text('des_type') + resolve_space(self.custom_info_type)
            result.append(BookFrame(text, 'text', {}))
            text = Get_text('des_info') + resolve_space(self.custom_info)
            result.append(BookFrame(text, 'text', {}))
        result.append(BookFrame(Get_text('des_document'), 'title', {}))
        result += self.document_info.get_description()
        text = Get_text('des_id_note')
        result.append(BookFrame(text, 'note', {}))

        return result




