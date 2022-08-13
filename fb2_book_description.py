
from fb2_book import get_tag_arguments, fb2_parser

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
                    self.patronimic = tag_text
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


class Date():
    def __init__(self) -> None:
        self.value = ''
        self.text = ''
    
    def parse(self, text:str, tag:str):
        real_tag, attr = get_tag_arguments(tag)
        if 'value' in attr:
            self.value = attr['value']
        self.text = text.strip()


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
        print('image - FB2_Tag, may contain a lot of pictures')
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


class Document_Info():
    def __init__(self) -> None:
        self.document_authors = []
        self.publishers = []
        self.program_used = ''
        self.program_used_id = ''
        self.document_date = Date()
        self.src_url = ''
        self.src_scanner_person = None
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


class Original_Info(Title_Info):
    def __init__(self) -> None:
        super().__init__()
        self.lang = 'unknown'
        self.src_lang = 'unknown'


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
                    self.document_info = Publish_info()
                    close_tag = text.find('</publish-info>',tag_end)
                    pos = close_tag + 15
                    content = text[tag_end+1:close_tag]
                    self.publish_info.parse(content)
                elif tag_text == 'src-title-info':
                    self.document_info = Original_Info()
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





